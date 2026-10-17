---
title: "Pocket Local — Rev 3: Searchable Chat Memory"
summary: "An offline chat knowledge base brings relevant older conversations into each reply, with memory controls and the keyboard layout fix retained."
date: 2026-10-17
author: Alex Blythe
tags: [Pocket Local, Android, Offline AI, Memory]
readingTime: 3 min
draft: false
relatedSoftware: [Pocket Local]
product: Pocket Local
version: "Rev 3 · v1.1.0"
releaseUrl: https://github.com/alexthegreat714/alex-blythe-site/releases/tag/pocket-local-v1.1.0
---

**Rev 3 is available to download.** Pocket Local now saves chat history into a searchable knowledge base on your phone and retrieves relevant passages before generating a reply. The previous keyboard layout fix is included: the composer resizes with the app above the keyboard.

**[Download the Rev 3 Android APK — about 645 MB](https://github.com/alexthegreat714/alex-blythe-site/releases/download/pocket-local-v1.1.0/Pocket-Local-1.1.0-arm64-v8a.apk)**

Prefer an archive? [Download the offline ZIP](https://github.com/alexthegreat714/alex-blythe-site/releases/download/pocket-local-v1.1.0/Pocket-Local-1.1.0-offline.zip), extract it, then install the APK inside. The app version is **1.1.0**, Android revision code **3**. The full model is included in both downloads.

## What changed

- **A local chat knowledge base.** Existing saved conversations migrate automatically into an on-device database. Messages are indexed as passages with links back to their source conversations.
- **Recall before each reply.** Keyword search looks through older turns and other saved chats. Relevant excerpts join the recent conversation so the assistant can refer to information that would otherwise have fallen out of its immediate context. Short follow-ups also use recent user turns to guide the search.
- **Visible memory.** Tap **Memory** below the composer to search saved chats, inspect the excerpts used for the last reply, and open their original conversations.
- **Controls for what gets recalled.** Use **Exclude / Remember** in History to control a chat's inclusion in the knowledge base. Settings can disable automatic retrieval while keeping history. Deleting a conversation removes its indexed passages too.
- **Keyboard layout fix retained.** The app handles Android keyboard insets and resizes the chat view; the compact layout also keeps the composer and Memory control visible at reduced heights.

## How the memory works

This is retrieval-augmented generation: save, search, then include useful excerpts in the next prompt. Search uses BM25 keyword matching entirely on the phone. The app fits recent turns and up to four retrieved passages into the model's existing **2,048-token context**, using the model's native tokenizer to count tokens. Retrieved memory has a **400-token budget**.

The model does not retrain itself or gain a larger context window. Retrieval helps it reuse selected information from a much longer history, but keyword search can miss paraphrases and recall is not guaranteed. Retrieved assistant statements are marked as unverified; the prompt favors newer user corrections.

Pocket Local still runs **Qwen3 0.6B Q8_0** through llama.cpp on the phone's CPU. Chats and the knowledge base stay in app storage. No account, network permission, telemetry, or desktop connection is required. This app is separate from the Aero fine-tune.

## Install without losing your chats

Download the APK on your Android phone and **install it over the existing Pocket Local app**. Do not uninstall it or clear its storage first. The package and signing certificate are unchanged, allowing Android to preserve existing app data. Saved chats migrate on launch, and the prepared model is reused on a normal update.

For a fresh installation, allow about **1.5 GB of storage**, plus space for your chat history. Android may ask you to permit installation from your browser or file manager. See the [download and installation page](/downloads/pocket-local/) for details.

## Validation

Fourteen memory and storage tests passed. Browser checks covered the memory interface, settings persistence, and reduced-height layout. A synthetic recall check using the real model on a Windows CPU recovered a saved pet name from a different conversation. The signed ARM64 APK passed build, Android release lint, signature, bundled-model hash, and 16 KB alignment checks.

These checks do not establish general recall accuracy. Full Android integration and physical Galaxy S26 keyboard behavior, compatibility, and speed still need on-device confirmation.

[Validation record](https://github.com/alexthegreat714/alex-blythe-site/releases/download/pocket-local-v1.1.0/VALIDATION.json) · [Checksums](https://github.com/alexthegreat714/alex-blythe-site/releases/download/pocket-local-v1.1.0/SHA256SUMS.txt) · [Release and source download](https://github.com/alexthegreat714/alex-blythe-site/releases/tag/pocket-local-v1.1.0)
