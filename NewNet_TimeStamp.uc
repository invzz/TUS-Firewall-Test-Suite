class NewNet_TimeStamp extends ReplicationInfo;

var float ServerNow;
var float OffsetSrvMinusCli;
var float AverDT;
var float Alpha;
var bool  bOffsetInit;
var float ClientTimeStamp;
var float TimeSinceBegin; // For auto-adjusting Alpha

replication
{
    unreliable if (Role == ROLE_Authority)
        ServerNow, AverDT, ClientTimeStamp;
}


simulated function PostBeginPlay()
{
    Super.PostBeginPlay();
    Alpha = 0.30; // faster convergence after join
    TimeSinceBegin = 0.0;
}
simulated function Tick(float DeltaTime)
{
    local float Hard;
    if (Role == ROLE_Authority)
    {
        ServerNow = Level.TimeSeconds;
        return;
    }

    // Auto-adjust Alpha after 2 seconds
    TimeSinceBegin += DeltaTime;
    if (TimeSinceBegin > 2.0 && Alpha > 0.20)
        Alpha = 0.20;

    // harte, aktuelle Differenz
    Hard = ServerNow - Level.TimeSeconds;

    if (!bOffsetInit)
    {
        // Beim Join/Respawn einmal hart setzen
        OffsetSrvMinusCli = Hard;
        bOffsetInit = true;
        return;
    }

    // Wenn wir weit daneben liegen (z. B. nach Mapwechsel/Rejoin) ? hart nachziehen
    if (Abs(Hard - OffsetSrvMinusCli) > 0.20)
    {
        OffsetSrvMinusCli = Hard;
    }
    else
    {
        // sonst weich glätten
        OffsetSrvMinusCli = (1.0 - Alpha) * OffsetSrvMinusCli + Alpha * Hard;
    }
}

function ReplicatetimeStamp(float f)
{
    ClientTimeStamp=f;
}

function ReplicatedAverDT(float f)
{
    AverDT = f;
}

defaultproperties
{
    NetUpdateFrequency=200.0
    NetPriority=5.0
    bAlwaysRelevant=True
}
