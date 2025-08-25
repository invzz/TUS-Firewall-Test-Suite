# NewNet_SniperRifle & NewNet_TimeStamp for UT2004

## Overview
This project provides a custom sniper rifle for Unreal Tournament 2004 with improved netcode, as well as a supporting timestamp synchronization class. The goal is to provide more accurate hit registration and fairer gameplay in online matches, especially under varying network conditions.

---

## Classes

### `NewNet_SniperRifle`
**Extends:** `SniperRifle`

A custom sniper rifle that uses enhanced client-server synchronization for firing logic. It disables the default enhanced netcode and implements its own system for more precise shot registration.

#### Key Logic & Functions
- **Structs `ReplicatedRotator` & `ReplicatedVector`:**
  Used to replicate rotation and position data efficiently between client and server.

- **`DisableNet()`:**
  Disables enhanced netcode for this weapon by setting a flag in the fire mode.

- **`PostBeginPlay()`:**
  Initializes configuration and caches a reference to the `NewNet_TimeStamp` actor for performance.

- **`RateSelf()`, `BringUp()`, `PutDown()`:**
  Standard weapon lifecycle functions, with null checks for safety.

- **`SpawnLGEffect()`:**
  Spawns a lightning gun effect at the hit location. Warns if called on the server (should be client-only).

- **`ClientStartFire()`:**
  Handles client-side fire input. If using the new netcode, delegates to `NewNet_ClientStartFire`.

- **`NewNet_ClientStartFire()`:**
  Main client-side firing logic. Gathers the player's view and position, calculates the time offset between client and server, and sends a fire request to the server. Uses the raw server-client time difference for best accuracy.

- **`AltReadyToFire()`:**
  Checks if the weapon is ready to fire, considering alternate fire modes and cooldowns.

- **`GetWeightedPing()`, `CalcSoftmaxPuffer()`:**
  Functions to calculate ping compensation and buffer times for fairer hit registration.

- **`NewNet_ServerStartFire()`:**
  Main server-side fire handler. Rewinds the server state to match the client's shot time, applies ping and buffer compensation, and validates the shot. Logs debug info if enabled.

- **`IsReasonable()`:**
  Checks if the client-reported position is within a reasonable threshold of the server's view, to prevent cheating or desync.

---

### `NewNet_TimeStamp`
**Extends:** `ReplicationInfo`

A helper class for synchronizing the server and client clocks. Used by the sniper rifle to calculate accurate time offsets for lag compensation.

#### Key Logic & Functions
- **Variables:**
  - `ServerNow`: The current server time.
  - `OffsetSrvMinusCli`: The calculated offset between server and client clocks.
  - `AverDT`: Average delta time (for smoothing).
  - `Alpha`: Smoothing factor for offset adjustment.
  - `bOffsetInit`: Whether the offset has been initialized.
  - `ClientTimeStamp`: The last timestamp sent from the client.

- **Replication:**
  Replicates key timing variables from server to client for synchronization.

- **`PostBeginPlay()`:**
  Initializes the smoothing factor (`Alpha`).

- **`Tick(float DeltaTime)`:**
  Updates the server time and calculates the offset between server and client. Smooths the offset over time for stability, but can snap to the correct value if a large discrepancy is detected (e.g., after map change).

- **`ReplicatetimeStamp(float f)`, `ReplicatedAverDT(float f)`:**
  Functions to update replicated timing variables.

---

## Netcode Improvements
- Uses raw server-client time difference for lag compensation, improving hit accuracy.
- Caches references and uses local variables to minimize performance overhead.
- Debug logging is optional and controlled by a flag.
- Designed to be robust against network jitter and high ping.

---

## Usage
- Place both `.uc` files in your UT2004 mod's source directory.
- Compile with UnrealScript tools.
- Set `bDebug` to `true` in `NewNet_SniperRifle` if you want detailed debug logs.

---

## Credits
- Original code and optimizations by project author.
- Offset calculation fix and suggestions by contributor/friend.
