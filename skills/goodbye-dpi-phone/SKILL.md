---
name: goodbye-dpi-phone
description: "Guide for configuring GoodbyeDPI-style DPI bypass on Android phones. Trigger when user asks about bypassing DPI censorship on mobile, setting up GoodbyeDPI on Android, or configuring anti-censorship tools for phones."
license: Apache 2.0
---

# GoodbyeDPI for Phone — Setup Guide

This skill provides instructions for setting up DPI (Deep Packet Inspection) bypass on Android phones using open-source tools.

## Overview

GoodbyeDPI is an open-source utility that bypasses DPI-based internet censorship. On Android, the equivalent app is **GoodbyeDPI Android** (also known as "ByeDPI" for Android), which provides similar functionality without requiring root access.

## Android Setup (No Root Required)

### Option 1: ByeDPI (Recommended)

ByeDPI is a lightweight Android app that creates a local VPN to bypass DPI filtering.

1. **Download** the latest release of ByeDPI from its GitHub releases page (`dovecoteescapee/ByeDPIAndroid`)
2. **Install** the APK on your Android device
3. **Open** the app and tap **Connect**
4. **Accept** the VPN connection prompt — it creates a local proxy (no remote server involved)

#### Configuration Options

- **Default mode**: Works out of the box for most DPI systems
- **Settings** → **DPI bypass mode**: Choose between:
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

PowerTunnel is another open-source anti-censorship tool with an Android client.

1. **Download** PowerTunnel for Android from its GitHub releases (`krlvm/PowerTunnel-Android`)
2. **Install** and open the app
3. **Enable** the connection — it also works via local VPN
4. **Configure** DPI circumvention options under Settings:
   - Enable chunking (splits HTTP requests)
   - Set chunk size (recommended: 2-5)
   - Enable MIX Host (mixed-case domain headers)
   - Enable dot after host (appends dot to Host header)

### Option 3: DPITunnel

DPITunnel is specifically designed for Android DPI bypass.

1. **Download** from GitHub releases (`nomoresat/DPITunnel-android`)
2. **Install** and launch the app
3. **Select** your ISP profile or use auto-detect
4. **Start** the tunnel

## Troubleshooting

### Connection not working after enabling

- Try switching DPI bypass modes (e.g., from `desync_first` to `disorder`)
- Increase the TTL value for fake packets (try 2-8)
- Change the split position (try values between 1-10)
- Some ISPs require combining multiple techniques

### Specific sites still blocked

- Enable SNI spoofing for HTTPS-blocked sites
- Try the `fake` desync mode with a low TTL
- Use a custom split position matching the SNI offset in the TLS ClientHello

### Battery drain

- ByeDPI and similar local VPN tools have minimal battery impact since traffic stays on-device
- If battery drain is noticeable, check if other apps are routing excessive traffic through the VPN

### App conflicts

- Only one VPN app can be active at a time on Android
- Disable other VPN apps before enabling the DPI bypass tool
- Some antivirus apps may flag local VPN tools — add an exception if needed

## Guidelines

- These tools are **open-source** and use **local proxies only** — no remote servers are involved
- They work by manipulating packet structure to prevent DPI systems from identifying and blocking traffic
- **No root access** is required for any of the recommended tools
- Always download apps from their official GitHub release pages to avoid tampered versions
- These tools are intended for accessing legitimately available content that is incorrectly blocked by overly aggressive DPI systems

## How It Works (Technical)

DPI bypass tools exploit weaknesses in how DPI systems inspect packets:

1. **TCP segmentation**: Split the TLS ClientHello across multiple TCP segments so the DPI cannot read the SNI field in a single pass
2. **Fake packets**: Send decoy packets with low TTL that reach the DPI but not the destination server, confusing the inspection
3. **Out-of-order delivery**: Send TCP segments in reverse order — the destination reassembles them correctly, but the DPI may fail to
4. **Host header manipulation**: For HTTP, modify the Host header formatting (mixed case, extra dots) to bypass pattern matching
