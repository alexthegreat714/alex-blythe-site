---
title: "Pocket Local — Rev 4: Persistent Update Cleanup"
summary: "Update in place, retain your chats, and clean obsolete app files and older installers in a folder you authorize once."
date: 2026-10-17
author: Alex Blythe
tags: [Pocket Local, Android, Offline AI, Storage]
readingTime: 3 min
draft: false
relatedSoftware: [Pocket Local]
product: Pocket Local
version: "Rev 4 · v1.2.0"
releaseUrl: https://github.com/alexthegreat714/alex-blythe-site/releases/tag/pocket-local-v1.2.0
---

**Rev 4 adds persistent cleanup to keep old revision files from accumulating.** Install it over your existing Pocket Local app, then open it to run cleanup. Your conversations, searchable knowledge base, settings, and current prepared model are retained.

**[Download the Rev 4 Android APK — about 645 MB](https://github.com/alexthegreat714/alex-blythe-site/releases/download/pocket-local-v1.2.0/Pocket-Local-1.2.0-arm64-v8a.apk)**

This is **version 1.2.0, Android revision code 4**, signed with the same certificate and using the same package ID as earlier releases. **Do not uninstall or clear app storage before updating.** The [full download page](/downloads/pocket-local/) includes an optional offline ZIP, source, checksums, and installation instructions.

## Automatic app cleanup

Android replaces the installed package when you update. Pocket Local now also checks its own setup files on every launch. It removes obsolete standalone model files, interrupted model setup files, and recognized older Pocket Local installers in its private files directory. It keeps the current model at the same path, reusing it when unchanged. The WebView resource cache is cleared once per app version without clearing chats, IndexedDB, or settings.

Cleanup runs again on later launches, so a failed removal can be retried. The version comparison reads the installed package version automatically; the policy carries forward into future revisions.

## Set up downloaded-installer cleanup once

Downloaded APKs and ZIPs are separate from the installed app. To let Pocket Local clean older installers automatically:

1. Open **Settings → Storage & updates → Choose cleanup folder**.
2. Create or select a local folder named **PocketLocal**, for example inside Downloads, and allow access in Android's folder picker.
3. Keep or move your Pocket Local APK/ZIP downloads into that folder.

The app saves that folder permission for normal updates and restarts. Each launch removes recognized Pocket Local installer files **older than the installed version** from that folder. It keeps current/newer installers, unrelated files, and subfolders. **Clean now** retries immediately; the panel reports reclaimed space. **Disconnect folder** removes the saved access.

Android 11 and later do not allow selecting the top-level Downloads directory. Old installers elsewhere need removal in your Files app, or you can move them into the authorized PocketLocal folder. If the folder is moved, deleted, or its permission is revoked, select it again. See [Android's folder-access documentation](https://developer.android.com/training/data-storage/shared/documents-files) for these platform rules. No broad storage permission is added.

## Storage expectations

This remains a full offline APK, not a binary delta download. The app and its prepared model still need about **1.5 GB**, plus conversation history. Rev 4 prevents obsolete files from accumulating; it does not remove the model needed to run the assistant. Download the APK alone if you do not need the optional ZIP, to avoid retaining another installer copy.

Rev 3's searchable chat memory and the keyboard layout fix are retained. Inference stays on the phone with no account, telemetry, or network permission.

## Validation

Eighteen Java storage-policy checks passed, covering old/current/future versions, preservation of user data and the current model, non-recursive cleanup, and repeated launches. All fourteen memory/storage tests still pass. The new storage panel was checked in a browser. The signed ARM64 build passed Android release lint, signature, bundled-model hash, and 16 KB alignment checks.

The Android folder picker, persisted grants, provider deletion, in-place phone upgrade, and physical Galaxy S26 behavior still need on-device confirmation. Browser and filesystem tests do not establish those results.

[Validation record](https://github.com/alexthegreat714/alex-blythe-site/releases/download/pocket-local-v1.2.0/VALIDATION.json) · [Checksums](https://github.com/alexthegreat714/alex-blythe-site/releases/download/pocket-local-v1.2.0/SHA256SUMS.txt) · [Release and source](https://github.com/alexthegreat714/alex-blythe-site/releases/tag/pocket-local-v1.2.0) · [Rev 3 notes](/updates/pocket-local-rev-3/)
