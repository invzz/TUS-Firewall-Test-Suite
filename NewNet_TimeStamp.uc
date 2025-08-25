class NewNet_TimeStamp extends ReplicationInfo;

var float ServerNow;
var float OffsetSrvMinusCli;
var float AverDT;
var float Alpha;
var bool  bOffsetInit;
var float ClientTimeStamp;

replication
{
    unreliable if (Role == ROLE_Authority)
        ServerNow, AverDT, ClientTimeStamp;
}


simulated function PostBeginPlay()
{
    Super.PostBeginPlay();
    Alpha = 0.30; // schnelleres Einfangen nach Join
    // du kannst nach ~2 Sekunden wieder auf 0.20 runtersetzen
}
simulated function Tick(float DeltaTime)
{	 local float Hard;
    if (Role == ROLE_Authority)
    {
        ServerNow = Level.TimeSeconds;
        return;
    }

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
        // Tipp: Alpha die ersten ~2s größer (0.30), danach 0.15–0.20
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
