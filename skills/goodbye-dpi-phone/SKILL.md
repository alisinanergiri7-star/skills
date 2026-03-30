---
name: goodbye-dpi-phone
description: "Guide for configuring GoodbyeDPI-style DPI bypass on iPhone (iOS) and Android phones. Trigger when user asks about bypassing DPI censorship on mobile, setting up GoodbyeDPI on iPhone/Android, or configuring anti-censorship tools for phones."
icon: assets/icon.svg
license: Apache 2.0
---

# GoodbyeDPI for Phone — Setup Guide

This skill provides instructions for setting up DPI (Deep Packet Inspection) bypass on **iPhone (iOS 18+/iPhone 17)** and Android phones using open-source tools.

## GoodbyeDPI: PC vs Phone — How Do They Compare?

| Feature | PC (GoodbyeDPI) | iPhone (iOS) | Android |
|---------|-----------------|--------------|---------|
| Packet manipulation | Direct via WinDivert driver | Via local VPN/Network Extension | Via local VPN |
| Root/Admin required | Yes (admin) | No (uses VPN API) | No |
| DPI desync modes | Full (fake, split, disorder, OOB, etc.) | Limited (depends on app) | Full (via ByeDPI) |
| Works on HTTPS (TLS) | Yes | Yes | Yes |
| Works on HTTP | Yes | Yes | Yes |
| System-wide | Yes | Yes (VPN covers all traffic) | Yes (VPN covers all traffic) |
| Performance impact | Minimal | Minimal | Minimal |
| Open source | Yes | Partial (some apps) | Yes |

**Key difference**: On PC, GoodbyeDPI hooks directly into the network stack via a kernel driver (WinDivert). On phones, the same packet manipulation techniques are wrapped inside a **local VPN tunnel** — traffic never leaves your device to a remote server. The underlying DPI bypass methods (TCP segmentation, fake packets, out-of-order delivery) are **identical** to the PC version.

## iPhone 17 / iOS Setup

iOS is more restrictive than Android — apps cannot freely manipulate packets. DPI bypass on iPhone works through the **Network Extension / VPN API**, which Apple allows on the App Store.

### Option 1: ByeDPI for iOS (Recommended)

A port of the ByeDPI engine to iOS, using the Network Extension framework.

1. **Search** for "ByeDPI" on the App Store (or install via TestFlight if not yet on the App Store)
2. **Open** the app and go to **Settings**
3. **Select** a DPI bypass mode:
   - `desync_first` — splits the first TLS ClientHello
   - `split` — TCP segment splitting
   - `disorder` — out-of-order TCP segments
   - `fake` — sends fake packet with low TTL
4. **Tap Connect** — accept the VPN configuration prompt
5. You'll see a VPN icon in the status bar when active

#### Recommended Settings for iPhone 17

| Setting | Recommended Value | Notes |
|---------|-------------------|-------|
| Bypass mode | `disorder` or `fake` | Try `disorder` first |
| Split position | 2 | Increase to 3-5 if needed |
| Fake packet TTL | 1-3 | Start with 1, increase if blocked |
| SNI spoofing | Off | Enable only if specific sites are blocked |

### Option 2: Shadowrocket + DPI Bypass

Shadowrocket is a paid ($2.99) but powerful network tool available on the App Store.

1. **Purchase and install** Shadowrocket from the App Store
2. **Add a local proxy**:
   - Type: **SOCKS5** or **HTTP**
   - Server: `127.0.0.1`
   - Port: `1080`
3. **Enable** the advanced settings:
   - Go to **Settings** → **Advanced**
   - Enable **TCP Segmentation**
   - Set segment size to **2-5**
4. **Connect** — Shadowrocket creates a local VPN

### Option 3: Psiphon

Psiphon is a free, open-source anti-censorship tool available on the App Store.

1. **Download** Psiphon from the App Store
2. **Open** and tap **Start**
3. It automatically selects the best bypass protocol
4. Note: Psiphon routes traffic through its servers (unlike local-only tools above)

### Option 4: DNS-Based Bypass (Built-in, No App Needed)

Some DPI systems only inspect DNS queries. iOS has built-in encrypted DNS support:

1. **Go to** Settings → Wi-Fi → tap your network → **Configure DNS**
2. **Select** Manual and add encrypted DNS servers:
   - `1.1.1.1` and `1.0.0.1` (Cloudflare)
   - `8.8.8.8` and `8.8.4.4` (Google)
3. **Or** install a DNS profile:
   - Visit `one.one.one.one` in Safari
   - Download the **DNS over HTTPS** configuration profile
   - Go to Settings → General → VPN & Device Management → install the profile
4. This encrypts DNS queries so DPI cannot see which domains you're requesting

> **Note**: DNS-only bypass won't work if your ISP does deep packet inspection on TLS/SNI. Use Option 1 or 2 for full bypass.

## Android Setup (No Root Required)

### Option 1: ByeDPI (Recommended)

1. **Download** the latest APK from GitHub releases (`dovecoteescapee/ByeDPIAndroid`)
2. **Install** and open the app, tap **Connect**
3. **Accept** the VPN prompt — local proxy only, no remote server

#### Configuration Options

- **Settings** → **DPI bypass mode**:
  - `desync_first` — splits the first TLS ClientHello packet
  - `desync_zero` — sends a zero-length packet before the real one
  - `split` — splits TCP segments
  - `disorder` — sends TCP segments out of order
  - `fake` — sends a fake packet before the real one

#### Advanced Settings

| Setting | Description | Default |
|---------|-------------|---------|
| Split position | Byte offset to split the packet | 2 |
| TTL for fake packets | Time-to-live for decoy packets | 1 |
| Use SNI spoofing | Replace SNI in ClientHello | Off |
| Custom SNI | Domain to use for spoofing | — |

### Option 2: PowerTunnel for Android

1. **Download** from GitHub releases (`krlvm/PowerTunnel-Android`)
2. **Install** and open, enable the connection
3. **Configure** under Settings:
   - Enable chunking (splits HTTP requests)
   - Set chunk size (recommended: 2-5)
   - Enable MIX Host (mixed-case domain headers)
   - Enable dot after host (appends dot to Host header)

### Option 3: DPITunnel

1. **Download** from GitHub releases (`nomoresat/DPITunnel-android`)
2. **Install** and launch, select your ISP profile or auto-detect
3. **Start** the tunnel

## Troubleshooting

### iPhone-Specific Issues

#### VPN keeps disconnecting
- Go to Settings → General → VPN & Device Management → ensure the VPN config is set to **Connect On Demand** (if the app supports it)
- Disable Low Power Mode — iOS may kill VPN background processes
- Make sure Background App Refresh is enabled for the DPI bypass app

#### App not available on App Store
- Some DPI bypass apps are region-restricted on the App Store
- Switch your App Store region, or use TestFlight links from the project's GitHub page
- For ByeDPI iOS, check the GitHub repository for the latest TestFlight invite link

#### Cellular vs Wi-Fi
- Some ISPs apply different DPI rules on cellular vs Wi-Fi
- If bypass works on Wi-Fi but not cellular (or vice versa), try a different bypass mode
- On iPhone 17, both Wi-Fi 7 and 5G traffic go through the VPN tunnel

### General Issues

#### Connection not working after enabling
- Switch DPI bypass modes (e.g., `desync_first` → `disorder` → `fake`)
- Increase TTL for fake packets (try 2-8)
- Change split position (try 1-10)
- Some ISPs require combining multiple techniques

#### Specific sites still blocked
- Enable SNI spoofing for HTTPS-blocked sites
- Try `fake` desync mode with low TTL
- Use a custom split position matching the SNI offset in the TLS ClientHello

#### Battery drain
- Local VPN tools have minimal battery impact — traffic stays on-device
- If noticeable, check if other apps route excessive traffic through the VPN

#### App conflicts
- Only one VPN can be active at a time on both iOS and Android
- Disable other VPNs before enabling the DPI bypass tool

## Guidelines

- These tools use **local proxies only** — no remote servers involved (except Psiphon)
- They manipulate packet structure to prevent DPI from identifying and blocking traffic
- **No jailbreak or root** is required
- Always download from official App Store listings or GitHub release pages
- These tools are intended for accessing legitimately available content that is incorrectly blocked by overly aggressive DPI systems

## How It Works (Technical)

DPI bypass tools exploit weaknesses in how DPI systems inspect packets — **the same techniques work on PC and phone**:

1. **TCP segmentation**: Split the TLS ClientHello across multiple TCP segments so the DPI cannot read the SNI field in a single pass
2. **Fake packets**: Send decoy packets with low TTL that reach the DPI but not the destination server, confusing the inspection
3. **Out-of-order delivery**: Send TCP segments in reverse order — the destination reassembles them correctly, but the DPI may fail to
4. **Host header manipulation**: For HTTP, modify the Host header formatting (mixed case, extra dots) to bypass pattern matching

### PC vs Phone Architecture

```
PC (GoodbyeDPI):
  App → WinDivert Driver → packet manipulation → network

Phone (ByeDPI etc.):
  App → Local VPN Tunnel → packet manipulation → network
```

The packet manipulation layer is identical — only the hook point differs. On PC it's a kernel driver; on phone it's a VPN tunnel that intercepts traffic before it leaves the device.
