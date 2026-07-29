---
name: ecommerce-visual-system
description: Create ecommerce product visual systems for TikTok Shop, overseas TT Shop, Amazon-style PDPs, Shopify listings, and social commerce launches. Use when the user asks for 电商视觉体系, 商品九宫格, TikTok Shop/TT小店商品图, 主图/详情图组, shoppable photo sets, or a connected long-scroll product visual story. Proactively ask for product/reference images, generate a main image anchor first, require user confirmation of that main image, then offer to generate the visual system as one master nine-grid or long-strip image and crop it locally. Always ask the user to choose between a nine-image grid and a connected long-strip narrative unless they already specify one; when the project requires OKM, generate images only through the OKM image API.
---

# Ecommerce Visual System

## Core Rule

Before generating images, collect a product/reference image unless the user already provided one. Use the reference image to lock shape, style direction, composition, material, and product identity. If the user has no image, ask for one and explain that it improves consistency; continue without it only if they explicitly choose text-only generation.

Offer exactly two structure choices unless the user already chose one:

1. Nine-image grid: separate square PDP images for marketplace upload.
2. Connected long-strip narrative: a visually linked sequence for TikTok Photo Mode, Xiaohongshu, landing pages, or detail-page storytelling.

Always generate the visual system in this order:

1. Main image anchor: one clean PDP hero image that locks the product shape, palette, material, surface artwork, logo/text placement, accessories, and camera/angle language.
2. User confirmation: show the main image anchor and ask the user to approve it before generating any visual-system master.
3. Visual-system prompt: after approval, proactively ask whether to generate the full visual set now; if yes, continue with the selected structure.
4. Visual-system master: one generated 3x3 grid master or one generated connected long-strip master, based on the user's selected structure.
5. Local crops: crop the master into upload-ready individual images or panels.

If the user says "both", produce the main image anchor once, then produce the nine-grid master first and derive the long-strip master from the same anchor.

## OKM Requirement

When the user says OKM is required, or the project memory/context says all image generation must use OKM:

- Use OKM only for image generation.
- Do not use local Pillow/canvas synthesis as a substitute for model generation.
- Do not invoke unrelated image generation skills or providers.
- Use the raw HTTP OKM route or the bundled script in `scripts/generate_okm_images.py`.
- Load keys from environment or `~/.codex/auth.json`; never print or write API keys into project files.
- Generate visual-system masters in one OKM request per structure to reduce image-generation cost; do not default to one OKM request per PDP slot.

Default OKM settings:

- Base URL: `https://okmcode.com/v1/images/generations`
- Model: `gpt-image-2`
- Size: `1024x1024` for marketplace grids
- Quality: `high`
- Headers: `Authorization: Bearer <key>`, `Content-Type: application/json`, `Accept: application/json`, `User-Agent: codex-cli`

## Workflow

1. Collect reference inputs and clarify structure.
   - If the user has not provided a product/reference image, ask them to upload one before generating.
   - If they already provided images, label each role: product reference, style reference, composition reference, or edit target.
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
   - First create a single main-anchor job named `01_main_anchor`.
   - Run `scripts/generate_okm_images.py --jobs <main_jobs.json> --out <main_output_dir> --size 1024x1024 --quality high --reference-image <reference_path> --reference-mode auto` when a reference image exists.
   - Inspect the main image. If the product shape is incomplete, the artwork moved into the background, or marketplace cleanliness fails, regenerate the main image before showing it as the anchor.
   - Show the main image anchor to the user and ask for approval. Do not generate a visual-system master until the user clearly approves the main image.
   - After approval, prompt: "主图确认通过。要继续生成九宫格成套视觉图，还是一排长图？" Use the previously selected structure if one already exists.
   - Then create one visual-system master job: `visual_grid_master` for nine grids or `visual_strip_master` for long strips.
   - In the visual-system prompt, explicitly state: `same product as the main image, consistent material, colorway, camera bumper, accessory/charm, silhouette, and proportions`.
   - Prefer passing the main image with `--reference-image <main_image_path> --reference-mode auto`. If the API does not support image references, the script will fall back to a text anchor.
   - For nine grids, run with `--crop-layout grid3x3`; for long strips, run with `--crop-layout strip7`.
   - Use `--dry-run` before generation when you need to validate jobs, crop layout, or reference-image wiring without calling OKM.
   - Inspect the master and local crops. Regenerate the master if the product design changes, the grid/panel boundaries are unusable, brand text is badly distorted, or marketplace cleanliness is violated.

5. Deliver the system.
   - Provide the main image anchor, master image, local crops, contact sheet, and a concise visual-system note.
   - State that OKM was used, including model/size/quality, without exposing credentials.

## Confirmation Gate

Treat only clear approval as permission to continue from the main image anchor to the visual-system master, for example: "确认", "通过", "可以", "继续生成成套视觉", "approved", or equivalent. If the user requests changes, revise the main image anchor first and ask for confirmation again.

## Prompt Rules

- Put exact product text in quotes, for example: `Brand text must read exactly "HIVE"`.
- Repeat critical spatial constraints: `artwork printed on the case surface, not placed in the background`.
- For PDP images, specify: clean white or pale background, no props unless the image role calls for them, no overlay text, no watermark.
- For lifestyle images, keep the product as the hero and use low-clutter realistic scenes.
- For detail images, crop into material, edge, camera lip, texture, closure, bundle, or scale.
- For long-strip narratives, keep visual continuity: same product, same palette, progressive camera distance, and one clear role per panel.
- For visual-system masters, require clear grid or panel separation and keep important product content away from crop boundaries.

## Output Naming

Use stable filenames:

- `01_main_anchor`
- `visual_grid_master`
- `visual_strip_master`

For cropped nine-grid outputs:

- `01_pdp_main_white`
- `02_angle_hero_clean`
- `03_on_product_art_detail`
- `04_material_macro`
- `05_lifestyle_hand`
- `06_packaging_bundle`
- `07_corner_protection_detail`
- `08_front_back_pair`
- `09_shoppable_photo_scene`

For cropped long-strip outputs:

- `01_hook`
- `02_product_reveal`
- `03_art_story`
- `04_material_detail`
- `05_lifestyle_use`
- `06_trust_bundle`
- `07_final_hold`
