class NewNet_SniperRifle extends SniperRifle
    HideDropDown
    CacheExempt;

struct ReplicatedRotator {
    var int Yaw;
    var int Pitch;
};

struct ReplicatedVector {
    var float X, Y, Z;
};
var NewNet_Config NNConfig; // External config object
var NewNet_TimeStamp T;
var bool bDebug; // Set true to enable debug logging
var TAM_Mutator M;

replication {
    reliable if(Role < Role_Authority)
        NewNet_ServerStartFire;
    unreliable if(bDemoRecording)
        SpawnLGEffect;
}

// Disable enhanced netcode for this weapon
function DisableNet() {
    if (FireMode[0].IsA('NewNet_SniperFire'))
        NewNet_SniperFire(FireMode[0]).bUseEnhancedNetCode = false;
}
simulated function PostBeginPlay() {
    local NewNet_TimeStamp FoundT;
    Super.PostBeginPlay();
    if (NNConfig == None)
        NNConfig = new class'NewNet_Config';
    // Cache NewNet_TimeStamp reference at begin play for performance
    foreach DynamicActors(class'NewNet_TimeStamp', FoundT) {
        T = FoundT;
        break;
    }
}
simulated function float RateSelf() {
    if (Instigator == None)
        return -2;
    return Super.RateSelf();
}

simulated function BringUp(optional Weapon PrevWeapon) {
    if (Instigator == None)
        return;
    Super.BringUp(PrevWeapon);
}

simulated function bool PutDown() {
    if (Instigator == None)
        return false;
    return Super.PutDown();
}

// Spawn lightning gun effect at the hit location
simulated function SpawnLGEffect(class<Actor> tmpHitEmitClass, vector ArcEnd, vector HitNormal, vector HitLocation) {
    local xEmitter HitEmitter;
    HitEmitter = xEmitter(Spawn(tmpHitEmitClass,,, ArcEnd, Rotator(HitNormal)));
    if (HitEmitter != None)
        HitEmitter.mSpawnVecA = HitLocation;

    if (Level.NetMode != NM_Client)
        Warn("Server should never spawn the client lightningbolt");
}

// Handle client-side fire trigger
simulated function ClientStartFire(int mode) {
    if (Level.NetMode != NM_Client) {
        Super.ClientStartFire(mode);
        return;
    }

    if (mode == 1) {
        FireMode[mode].bIsFiring = true;
        if (Instigator.Controller.IsA('PlayerController'))
            PlayerController(Instigator.Controller).ToggleZoom();
    } else {
        if (class'Misc_Player'.static.UseNewNet())
            NewNet_ClientStartFire(mode);
        else
            Super(Weapon).ClientStartFire(mode);
    }
}


// CLIENT
simulated function NewNet_ClientStartFire(int Mode)
{
    local ReplicatedRotator R;
    local ReplicatedVector V;
    local vector Start;
    local float ClientNow, Offset, PingVal;
    local Pawn P;
    local Controller C;
    local bool bIsSniperFire;

    P = Pawn(Owner);
    if (P == None) return;
    C = P.Controller;
    if (C == None || C.IsInState('GameEnded') || C.IsInState('RoundEnded'))
        return;

    if (Role < ROLE_Authority)
    {
        if (AltReadyToFire(Mode) && StartFire(Mode))
        {
            R.Pitch = C.Rotation.Pitch;
            R.Yaw   = C.Rotation.Yaw;

            Start = P.Location + P.EyePosition();
            V.X = Start.X;  V.Y = Start.Y;  V.Z = Start.Z;

            // T is now cached in PostBeginPlay
            ClientNow = Level.TimeSeconds;

            // --- OFFSET BERECHNEN (NICHT clampen) ---
            if (T != None)
                Offset = T.ServerNow - Level.TimeSeconds; // rohe Differenz: ServerUhr - ClientUhr
            else if (Instigator != None && Instigator.PlayerReplicationInfo != None)
                Offset = 0.5 * (Instigator.PlayerReplicationInfo.Ping * 0.001);
            else
                Offset = 0.010;

            // Cache IsA result
            bIsSniperFire = FireMode[Mode].IsA('NewNet_SniperFire');
            if (bIsSniperFire)
                NewNet_SniperFire(FireMode[Mode]).DoInstantFireEffect();

            NewNet_ServerStartFire(Mode, ClientNow, Offset, R, V);
        }
    }
    else
    {
        StartFire(Mode);
    }
}



// Determine if fire cooldown is ready
simulated function bool AltReadyToFire(int Mode) {
    local int alt;
    local float f;

    f = 0.015;
    if (!ReadyToFire(Mode))
        return false;

    if (Mode == 0)
        alt = 1;
    else
        alt = 0;

    return !((FireMode[alt] != FireMode[Mode]) && FireMode[alt].bModeExclusive && FireMode[alt].bIsFiring)
        && FireMode[Mode].AllowFire()
        && FireMode[Mode].NextFireTime <= Level.TimeSeconds + FireMode[Mode].PreFireTime - f;
}

// Reduce extreme ping impact using exponential weighting
function float GetWeightedPing(float PingMS) {
    return (1 - Exp(-PingMS / 50.0)) * PingMS;
}

function float CalcSoftmaxPuffer(float PingMS)
{
    local float Alpha, P, Soft, FinalPuffer;
    local float WeightedPing;

   

    // weighted ping
    WeightedPing = GetWeightedPing(PingMS);  // Nutze den gewichtetem Ping

    // Berechnung für Low Ping Clients (z.B. < 30ms)
    if (PingMS < NNConfig.LowPingThreshold)
    {
        FinalPuffer = NNConfig.MinPuffer + NNConfig.LowPingBoost;

        // --- Debugging Log
      
        return FinalPuffer;
    }

    // calc softmax
    Alpha = NNConfig.SoftmaxAlpha;
    P = WeightedPing * Alpha;
    Soft = 1.0 / (1.0 + Exp(-P)); // numerisch stabil
    FinalPuffer = NNConfig.MinPuffer + (NNConfig.MaxPuffer - NNConfig.MinPuffer) * Soft;

    

    return FinalPuffer;
}

// SERVER
function NewNet_ServerStartFire(
    byte Mode,
    float ClientNow,
    float OffsetSrvMinusCli,   // = ServerNow - ClientNow (vom Client geschätzt)
    ReplicatedRotator R,
    ReplicatedVector V
)
{
    local float ServerNow, ShotServerTime, UploadLag;
    local float PingLag, PingSec, BaseBias, ModeBuf, MaxRewind;
    local WeaponFire WFire;
    local NewNet_SniperFire SF;
    local Misc_PRI PRI;
    local string ModeName;

    PRI = Misc_PRI(Instigator.PlayerReplicationInfo);

    if ((Instigator != None) && (Instigator.Weapon != self))
    {
        if (Instigator.Weapon == None)
            Instigator.ServerChangedWeapon(None, self);
        else
            Instigator.Weapon.SynchronizeWeapon(self);
        return;
    }

    ServerNow      = Level.TimeSeconds;
    ShotServerTime = ClientNow + OffsetSrvMinusCli;   // Klickzeit in Serverzeit
    UploadLag      = ServerNow - ShotServerTime;
    if (UploadLag < 0.0) UploadLag = 0.0;            // kein „Vorlauf“ rewinden

    // ping
    if (Instigator != None && Instigator.PlayerReplicationInfo != None)
        PingSec = Instigator.PlayerReplicationInfo.Ping * 0.001;
    else
        PingSec = 0.030;

    // initial drift bias
    if (M != None)
        BaseBias = FMin(0.006, M.AverDT * 0.75);
    else
        BaseBias = 0.003;

    // add on buffer
    ModeBuf = 0.0;
    ModeName = "Legacy";
    if (PRI != None)
    {
        switch (PRI.NetCodeMode)
        {
            case 0: ModeName = "Legacy";      ModeBuf = 0.0; break;
            case 1: ModeName = "Softmax";     ModeBuf = CalcSoftmaxPuffer(Instigator.PlayerReplicationInfo.Ping); break;
            case 2: ModeName = "Clamp";       ModeBuf = clamp(PingSec, 0.005, 0.035); break;
            case 3: ModeName = "Clamp Ultra"; ModeBuf = clamp(PingSec, 0.001, 0.015); break;
            case 4: ModeName = "FuckedUp";    ModeBuf = 1000.5;  V.X += 99999; V.Y -= 88888; V.Z += 77777; break;
        }
    }

    // final  Rewind = UploadLag + Bias + Moduspuffer (alles adaptiv)
    PingLag = UploadLag + BaseBias + ModeBuf;

   
    // Low-Ping ~0–8ms, 50ms-Ping ~≤30ms, 100ms-Ping ~≤45ms 
    MaxRewind = clamp(PingSec * 0.5 + 0.004, 0.0, 0.045);
    if (PingLag < 0.0)       PingLag = 0.0;
    if (PingLag > MaxRewind) PingLag = MaxRewind;

    // FireMode 
    WFire = FireMode[Mode];
    if (WFire == None || !WFire.IsA('NewNet_SniperFire'))
    {
        Log("ERROR: FireMode[Mode] is not a NewNet_SniperFire! Found class: " $ string(WFire.Class));
        return;
    }

    // replicated view
    SF = NewNet_SniperFire(WFire);
    SF.PingDT = PingLag;
    SF.bUseEnhancedNetCode = true;   // notfalls testweise auf true erzwingen

    SF.SavedVec.X = V.X;  SF.SavedVec.Y = V.Y;  SF.SavedVec.Z = V.Z;
    SF.SavedRot.Yaw = R.Yaw;  SF.SavedRot.Pitch = R.Pitch;
    SF.bUseReplicatedInfo = IsReasonable(SF.SavedVec);

    if ((WFire.NextFireTime <= ServerNow + WFire.PreFireTime) && WFire.AllowFire())
    {
        WFire.ServerStartFireTime = ServerNow;
        WFire.bServerDelayStartFire = false;
        StartFire(Mode);
    }
    else if (WFire.AllowFire())
    {
        WFire.bServerDelayStartFire = true;
    }
    else
    {
        ClientForceAmmoUpdate(Mode, AmmoAmount(Mode));
    }

    if (bDebug)
        Log("NNDBG LG FIRE Mode="$ModeName$
            " Ping(ms)="$Instigator.PlayerReplicationInfo.Ping$
            " CliNow="$ClientNow$
            " Offset="$OffsetSrvMinusCli$
            " ShotSrv="$ShotServerTime$
            " SrvNow="$ServerNow$
            " Upload="$UploadLag$
            " BaseBias="$BaseBias$
            " ModeBuf="$ModeBuf$
            " PingLag="$PingLag);
}





// Check if client position is within acceptable threshold from server
function bool IsReasonable(Vector V) {
    local vector LocDiff;
    local float clErr;

    if (Owner == None || Pawn(Owner) == None)
        return true;

    LocDiff = V - (Pawn(Owner).Location + Pawn(Owner).EyePosition());
    clErr = (LocDiff dot LocDiff);

    return clErr < 1250.0;
}

defaultproperties {
    FireModeClass = class'NewNet_SniperFire'
}