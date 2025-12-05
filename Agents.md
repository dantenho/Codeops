# Agents & Personas

## 1. The Researcher (SocialMediaNode & NFTTrendNode)
**Role**: Market Intelligence Analyst
**Goal**: Identify high-potential trends, keywords, and aesthetics from social media (Reddit, YouTube, Twitter) and NFT marketplaces.
**Tools**: `praw`, `google-api-python-client`, `playwright`, `OpenSea API`.
**Memory**: Writes trend reports to `ChromaDB`.

## 2. The Strategist (SalesStrategyNode & RAGNode)
**Role**: Creative Director & Sales Manager
**Goal**: Synthesize research into a concrete art direction (prompt) and sales strategy (pricing, timing).
**Tools**: `Google Gemini`, `ChromaDB (RAG)`.
**Memory**: Reads from `ChromaDB`, writes `Strategy` object.

## 3. The Asset Manager (CivitAINode)
**Role**: Resource Specialist
**Goal**: Locate and download the best LoRAs, Checkpoints, and embeddings to match the Strategist's vision.
**Tools**: `CivitAI API`.
**Memory**: Caches model paths.

## 4. The Creator (ComfyUINode & Anime4KNode)
**Role**: Digital Artist
**Goal**: Generate high-fidelity images using complex ComfyUI workflows and upscale them for production.
**Tools**: `ComfyUI`, `Anime4K`.
**Memory**: Stores generated image paths.

## 5. The Critic (ClipEvalNode & GradioEvalNode)
**Role**: Quality Assurance & Curator
**Goal**: Objectively score images (CLIP Aesthetic) and facilitate human review.
**Tools**: `CLIP (OpenAI/LAION)`, `Gradio`.
**Memory**: Logs scores and human feedback.

## 6. The Publisher (GasTrackerNode & NFTMintNode)
**Role**: Blockchain Operator
**Goal**: Mint and list the approved assets when network conditions are optimal.
**Tools**: `Web3.py`, `Pinata (IPFS)`.
**Memory**: Logs transaction hashes.

## 7. The Coder (GoogleGenAINode)
**Role**: Systems Engineer
**Goal**: Dynamically generate code snippets or logic adjustments if the workflow encounters novel problems.
**Tools**: `Google Gemini`.
