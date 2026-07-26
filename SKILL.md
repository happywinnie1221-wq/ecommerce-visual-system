---
name: ecommerce-visual-system
description: Create ecommerce product visual systems for TikTok Shop, overseas TT Shop, Amazon-style PDPs, Shopify listings, and social commerce launches. Use when the user asks for 电商视觉体系, 商品九宫格, TikTok Shop/TT小店商品图, 主图/详情图组, shoppable photo sets, or a connected long-scroll product visual story. Always ask the user to choose between a nine-image grid and a connected long-strip narrative unless they already specify one; when the project requires OKM, generate images only through the OKM image API.
---

# Ecommerce Visual System

## Core Rule

Before generating images, offer exactly two structure choices unless the user already chose one:

1. Nine-image grid: separate square PDP images for marketplace upload.
2. Connected long-strip narrative: a visually linked sequence for TikTok Photo Mode, Xiaohongshu, landing pages, or detail-page storytelling.

If the user says "both", produce the nine-image grid first, then derive the long-strip storyboard from it.

## OKM Requirement

When the user says OKM is required, or the project memory/context says all image generation must use OKM:

- Use OKM only for image generation.
- Do not use local Pillow/canvas synthesis as a substitute for model generation.
- Do not invoke unrelated image generation skills or providers.
- Use the raw HTTP OKM route or the bundled script in `scripts/generate_okm_images.py`.
- Load keys from environment or `~/.codex/auth.json`; never print or write API keys into project files.

Default OKM settings:

- Base URL: `https://okmcode.com/v1/images/generations`
- Model: `gpt-image-2`
- Size: `1024x1024` for marketplace grids
- Quality: `high`
- Headers: `Authorization: Bearer <key>`, `Content-Type: application/json`, `Accept: application/json`, `User-Agent: codex-cli`

## Workflow

1. Clarify structure.
   - If missing, ask: "做九宫格，还是前后关联的一排长图？"
   - For overseas TikTok Shop product listings, recommend nine-image grid.
   - For social posts or detail-page storytelling, recommend connected long-strip narrative.

2. Extract visual DNA from product inputs.
   - Product type, brand name, exact in-image text, palette, material, surface pattern, target market, platform.
   - Distinguish product artwork from background styling. If the product has a printed pattern, state "printed on the product surface, not in the background" in every image prompt.

3. Build the image plan.
   - For nine-image grids, use `references/tt-shop-visual-patterns.md`.
   - For long-strip narratives, use the connected sequence pattern in the same reference.
   - Keep main marketplace images free from added overlay copy, badges, watermarks, borders, or promotional graphics.

4. Generate with OKM.
   - Create a JSON job list with `name` and `prompt` fields.
   - Run `scripts/generate_okm_images.py --jobs <jobs.json> --out <output_dir> --size 1024x1024 --quality high`.
   - Inspect every output visually. Regenerate any image where the product design moved into the background, brand text is badly distorted, or the image violates marketplace cleanliness.

5. Deliver the system.
   - Provide the output folder, contact sheet, individual image list, and a concise visual-system note.
   - State that OKM was used, including model/size/quality, without exposing credentials.

## Prompt Rules

- Put exact product text in quotes, for example: `Brand text must read exactly "HIVE"`.
- Repeat critical spatial constraints: `artwork printed on the case surface, not placed in the background`.
- For PDP images, specify: clean white or pale background, no props unless the image role calls for them, no overlay text, no watermark.
- For lifestyle images, keep the product as the hero and use low-clutter realistic scenes.
- For detail images, crop into material, edge, camera lip, texture, closure, bundle, or scale.
- For long-strip narratives, keep visual continuity: same product, same palette, progressive camera distance, and one clear role per panel.

## Output Naming

Use stable numbered filenames:

- `01_pdp_main_white`
- `02_angle_hero_clean`
- `03_on_product_art_detail`
- `04_material_macro`
- `05_lifestyle_hand`
- `06_packaging_bundle`
- `07_corner_protection_detail`
- `08_front_back_pair`
- `09_shoppable_photo_scene`

For long strips:

- `01_hook`
- `02_product_reveal`
- `03_art_story`
- `04_material_detail`
- `05_lifestyle_use`
- `06_trust_bundle`
- `07_final_hold`

