# PNG-Analyzer

A compact, research-oriented desktop application for pixel-level analysis, visualization and transformation of PNG images.  
PNG-Analyzer is designed as an educational / exploratory tool that makes low-level image processing techniques explicit and observable: color-space decompositions, chroma subsampling, JPEG encoding building blocks, and texture measures (Tamura). It is ideal for students, researchers or engineers who want to inspect how image processing primitives behave on real images and to produce figures and metrics for reports or demonstrations.

In the GRAPH folder of this project you will find demo tests of all the tools of PNG-Analyzer
---

Table of contents
- Summary (what it is and why it exists)
- Highlights and main features (quick bullet list)
- Technical deep dive (architecture, modules and algorithms)
- Design patterns and engineering choices
- Libraries & environment
- Project layout and main modules (file-level map)
- Academic / practical relevance and use cases
- Next steps and extension ideas

---

Summary 
- PNG-Analyzer is a local GUI application that helps you inspect, visualize and experiment with how images are represented and processed internally.
- Through an intuitive graphical interface you can:
  - view and compare common color representations (RGB, YCbCr, HSV),
  - generate per-channel histograms and scatter visualizations,
  - examine the effect of chroma subsampling (4\:4:4 → 4\:2:2 → 4\:2:0) and see memory tradeoffs,
  - convert an RGB image through the main stages of JPEG compression (color conversion, block partitioning, DCT, quantization) and export the result,
  - compute texture descriptors (Tamura directionality, contrast map, granularity) and visualize local maps.
- The tool favors explicit, pixel-level implementations; many operations are implemented directly (matrix operations, block DCT, quantization, local filters) to make algorithmic behavior obvious.

Why this project exists
- To deepen understanding of image representation and processing at a low level, complementing higher-level libraries.
- To produce figures, metrics and intuition useful in coursework, reports or research that relies on color and texture descriptors.
- To provide a compact, modular codebase that can be extended, instrumented or reused in teaching and prototyping.

---

Highlights and main features 
- Color analysis
  - RGB / YCbCr / HSV transformations and per-channel inspection.
    ![alt text](https://github.com/riccardobonagura/PNG-Analyzer/blob/giorno-1-optimization1/graphs/RGBsplit.png)
    ![alt text](https://github.com/riccardobonagura/PNG-Analyzer/blob/giorno-1-optimization1/graphs/YCbCr-split.png)
  
  - RGB histograms and HSV scatter comparisons.
    ![alt text](https://github.com/riccardobonagura/PNG-Analyzer/blob/giorno-1-optimization1/graphs/Istogrammi-RGB.png)
    ![alt text](https://github.com/riccardobonagura/PNG-Analyzer/blob/giorno-1-optimization1/graphs/WBscatter.png)

  - White-balance demo (Gray World).
    ![alt text](https://github.com/riccardobonagura/PNG-Analyzer/blob/giorno-1-optimization1/graphs/Screenshot%202025-12-09%20155508.png)
  
- Subsampling & visualization
  - 4\:4:4, 4\:2:2 and 4\:2:0 chroma subsampling implementations and a ready-to-draw subsampling comparison figure (with textual 4×4 matrix extracts and memory stats).
    ![alt text](https://github.com/riccardobonagura/PNG-Analyzer/blob/giorno-1-optimization1/graphs/Subsampling.png)
- JPEG pipeline (educational)
  - End-to-end JPEG encoding pipeline implemented up to the point of entropy export: color conversion, chroma subsampling, 8×8 padding, block splitting, 2D DCT, quantization, zigzag ordering and final block collection for export.
  - Multiple quantization tables (quality presets) and channel-specific handling.
- Texture analysis (Tamura measures)
  - Directionality (Sobel-based orientation histogram), local contrast map (Tamura contrast), and granularity detector (Laplacian + connected components).
    ![alt text](https://github.com/riccardobonagura/PNG-Analyzer/blob/giorno-1-optimization1/graphs/Tamura-Directionality.png)

- GUI-driven workflow
  - Tkinter-based interface orchestrated by a controller that returns matplotlib Figure objects for display. Widgets and dialogs allow guided selection of images, channels, dates for plotting and tool parameters.
    ![alt text](https://github.com/riccardobonagura/PNG-Analyzer/blob/giorno-1-optimization1/graphs/NavigationMap.png)
---

Technical deep dive

Architecture (high level)
- Pattern: Model – View – Controller (MVC)
  - Model: `model/image_model.py` + utility modules under `model/` hold image data and processing primitives; they expose processed arrays, channels and helper data structures.
  - Controller: `controller/app_controller.py` orchestrates operations requested by the UI, builds matplotlib figures and returns metrics (scalars + Figure objects).
  - View: `view/gui.py` (Tkinter) manages user interactions and displays figures produced by the controller.
- Supporting modules are grouped by responsibility:
  - `model/color_tools.py` — color-space conversions, manual HSV conversion, channel splitters, histogram helpers, white-balance.
  - `model/subsampling_tools.py` — 4:2:2 and 4:2:0 implementations, memory usage calculators, extract-center helpers.
  - `model/jpeg_pipeline.py` + `model/jpeg_tools.py` — the pedagogical JPEG pipeline and helper functions for padding, block splitting, DCT, quantization, zigzag and block-level encoding and export.
  - `model/texture_tools.py` — Tamura-based texture measures (directionality, contrast map, granularity).
  - `model/subsampling_figure.py` — prepares structured data for a matplotlib figure that compares original and subsampled images (title, memory footprint, matrix excerpts).
  - `controller/app_controller.py` — exposes high-level methods used by the GUI: figure builders, converter, and analysis routines.
  - `view/gui.py` — a feature-rich Tkinter front-end with toggle-driven canvases, meta-data display and interactions for all the analysis and conversion features.

Key algorithmic elements

1) Color conversions and channel handling
- RGB ↔ YCbCr conversions are implemented to expose luminance (Y) and chroma (Cb/Cr). Splitting functions return separate 2D arrays for each channel.
- Manual conversion to HSV (and channel splitting) is implemented for didactic purposes and to allow scatter visualizations of Hue vs Saturation vs Value.

2) Chroma subsampling (4\:2:2 and 4\:2:0)
- Implemented explicitly over arrays:
  - 4\:2:2: horizontal halving per pairs of columns (keeps one chroma sample per pair and duplicates it to reconstruct same-shape arrays).
  - 4\:2:0: block-wise 2×2 chroma sampling (top-left of each 2×2 block chosen and broadcast to block).
- Utilities compute the memory footprint of chroma channels under different subsampling modes to illustrate storage tradeoffs.
- `subsampling_figure.create_subsampling_figure` packs three dictionaries (original/422/420) containing images, titles and a textual 4×4 matrix for direct visualization in reports/figures.

3) JPEG pipeline essentials
- The pipeline (`jpeg_pipeline.jpeg_encode_image`) follows educational steps:
  - Convert input RGB to YCbCr.
  - Subsample chroma (4:2:0) and reduce chroma resolution for encoding.
  - Split into Y, Cb, Cr matrices and half-resolution chroma arrays for blocks.
  - Pad each channel to multiples of 8 with `jpeg_tools.pad_to_block_size`.
  - Split channels into 8×8 blocks and apply 2D DCT to each block (`dct_2d`, `apply_dct_to_blocks`).
  - Quantize DCT coefficients using selectable quantization tables (LUMA/CHROMA presets).
  - Rearrange quantized coefficients in zigzag order and gather blocks.
  - Export block collections and quantization tables into a bytes-like structure (the code hands final encoding details to a final exporter — entropy encoding may rely on libraries like `jpegio` for full compliance).
- Quantization tables are provided for multiple quality levels, making it straightforward to illustrate effects of quantization on the reconstructed image and on the frequency-domain coefficients.

4) Texture features (Tamura family)
- Directionality: compute Sobel gradients on a sparse sampled grid; accumulate absolute orientation histograms and compute a peak/mean ratio as the directionality score.
- Contrast map: sliding-window local statistics over the luminance channel (Y) compute local contrast per Tamura's formula (sigma / mean_abs^0.25) and yield a global contrast scalar plus a spatial contrast map.
- Granularity: Laplacian filtering followed by thresholding using a high percentile; connected components identify granules within size bounds and produce normalized granularity metrics and granule metadata (position + area).

Design & engineering notes
- Lazy figure creation: complex figures are created only on demand (lazy initialization) to keep the UI responsive.
- Strategy-like view selection: multiple visualization modes (RGB, YCbCr, HSV, custom) are selectable and implemented as modular figure builder functions.
- The code emphasizes explicit math and array manipulation—this makes it an excellent learning artifact because each step is visible and can be instrumented.

---

Design patterns & project practices
- MVC: clear separation between data/processing (Model), orchestration (Controller) and presentation (View).
- Singleton / lazy caches: controller/model instances and some singletons are used to cache loaded data and avoid redundant computations during a session.
- Factory-like helpers: centralized widget/figure creation functions simplify GUI layout and keep layout logic consistent.
- Strategy/plug-in style for visualization: adding another view (e.g., a new color inspection) is a matter of adding another builder function and connecting a button.
- Pipeline abstraction: JPEG encoding and texture extraction are organized as pipelines that take an image and return a predictable set of artifacts (bytes, scalar metrics, images), making them reusable in batch scripts or unit tests.


---

Libraries & environment
- Primary numeric & array library: numpy
- Visualization: matplotlib
- Computer vision & image filtering: OpenCV (cv2)
- JPEG analysis/IO (used for some entropy handling / interoperability): jpegio
- GUI: tkinter (standard library)
- Development platform note: project was executed on Python 3.12.3 under WSL/Ubuntu for best compatibility with jpegio.
- Other supporting Python packaging dependencies mentioned in the internal doc: scipy, pillow, packaging-related packages and matplotlib sub-deps (fonttools, kiwisolver, contourpy, cycler), etc.

---

## Class Diagram
![alt text](https://github.com/riccardobonagura/PNG-Analyzer/blob/giorno-1-optimization1/graphs/ClassDiagram.png)
Project layout (high-level, core modules)
- model/
  - color_tools.py — color conversions, histogram & channel helpers, white balance and HSV scatter utilities
  - image_model.py — central image state and convenience accessors (original vs current image, channel extraction, subsampling metadata)
  - jpeg_pipeline.py — high-level JPEG pipeline coordinating color conversion, subsampling and block encoding
  - jpeg_tools.py — low-level JPEG primitives (padding, DCT, quantization, zigzag)
  - subsampling_tools.py — implementations of 4:2:2 and 4:2:0 and supporting helpers
  - subsampling_figure.py — constructs structured data for comparison figures
  - texture_tools.py — Tamura directionality, contrast and granularity
- controller/
  - app_controller.py — application orchestration, figure construction and analysis entry points
- view/
  - gui.py — Tkinter GUI with a modular canvas architecture and hooks to show matplotlib figures
- tests/ (suggested in future) — unit tests and small sample images (not required to run here)
- docs/ (optional) — diagrams, screenshots and the dissertation-style doc you shared


## Dependencies:
![alt text](https://github.com/riccardobonagura/PNG-Analyzer/blob/giorno-1-optimization1/graphs/Dependencies.png)

---

Academic & practical relevance
- The codebase is a teaching and demonstration vehicle:
  - Makes explicit the math behind color spaces, DCT and quantization.
  - Shows practical implications of chroma subsampling in terms of memory and visual artifacts.
  - Exposes how texture descriptors (Tamura measures) can be computed from raw pixel data and used as features for image retrieval, indexing or research.
- Use-cases:
  - Coursework / lab exercises in digital image processing.
  - Generating figures and numerical evidence for reports or lectures.
  - Rapid prototyping and experimentation for research on color/texture-based similarity search.
 
 ![alt text](https://github.com/riccardobonagura/PNG-Analyzer/blob/giorno-1-optimization1/graphs/UseCases.png)
