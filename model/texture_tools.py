import numpy as np
from model import color_tools


def compute_directionality_grid(
        img: np.ndarray,
) -> tuple[float, np.ndarray]:
    """
    Calcola la direzionalità di Tamura per una immagine (array numpy).
    Se l'immagine è RGB, utilizza la componente Y di YCbCr come intensità luminosa.

    Args:
        img (np.ndarray): Immagine, array 2D (grayscale) o 3D (RGB).

    Returns:
        directionality (float): Valore scalare della direzionalità.
        hist (np.ndarray): Istogramma delle orientazioni.
    """
    bin_width_deg: int = 10
    grid_step: int = 8

    # RGB -> YCbCr, usa la componente Y come grigia
    ycbcr_img = color_tools.convert_rgb_to_ycbcr(img)
    img_gray = ycbcr_img[..., 0]

    # Campionamento griglia
    img_sampled = img_gray[::grid_step, ::grid_step]
    h, w = img_sampled.shape

    # Kernel Sobel
    Kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float)
    Ky = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype=float)

    gx = np.zeros((h, w), dtype=float)
    gy = np.zeros((h, w), dtype=float)
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            region = img_sampled[i - 1:i + 2, j - 1:j + 2]
            gx[i, j] = np.sum(region * Kx)
            gy[i, j] = np.sum(region * Ky)

    # Orientazioni in [0, π]
    orientations = np.arctan2(gy, gx)
    orientations = np.abs(orientations)

    # Bin regolari su [0, π]
    bin_width_rad = np.deg2rad(bin_width_deg)
    bin_edges = np.arange(0, np.pi + bin_width_rad, bin_width_rad)
    bins = len(bin_edges) - 1

    hist, _ = np.histogram(orientations[1:-1, 1:-1].flatten(), bins=bin_edges)

    # Direzionalità scalare
    peak = np.max(hist)
    mean_other = (np.sum(hist) - peak) / (bins - 1)
    directionality = peak / (mean_other + 1e-7)

    return directionality, hist


def tamura_contrast_map(image: np.ndarray) -> tuple[float, np.ndarray]:
    """
    Calcola il valore Tamura per il contrasto e genera la mappa di contrasto locale per un'immagine RGB.
    Lo slicing usa passo 8 sia orizzontale che verticale.
    """
    # Conversione RGB -> luminanza Y (formula esplicita)
    # RGB -> YCbCr, usa la componente Y come grigia
    ycbcr_img = color_tools.convert_rgb_to_ycbcr(image)
    Y = ycbcr_img[..., 0]
    win_size = 7
    pad = win_size // 2

    # Padding per bordi
    Y_pad = np.pad(Y, pad, mode='reflect')
    H, W = Y.shape
    contrast_map = np.zeros((H, W), dtype=np.float32)
    step = 8  # passo di slicing

    # Scorrimento per blocchi 8x8 (basso livello, didattico)
    for i in range(0, H, step):
        for j in range(0, W, step):
            # Estrai la finestra locale centrata su (i, j)
            i0 = i
            j0 = j
            patch = Y_pad[i0:i0 + win_size, j0:j0 + win_size]
            mu = np.mean(patch)
            sigma = np.std(patch)
            mean_abs = np.mean(np.abs(patch - mu))
            local_contrast = sigma / (mean_abs ** 0.25) if mean_abs > 0 else 0.0
            # Assegna local_contrast all'intero blocco step x step
            contrast_map[i0:i0 + step, j0:j0 + step] = local_contrast

    # Contrasto Tamura globale (su tutta l'immagine)
    mu_global = np.mean(Y)
    sigma_global = np.std(Y)
    mean_abs_global = np.mean(np.abs(Y - mu_global))
    contrast_value = sigma_global / (mean_abs_global ** 0.25) if mean_abs_global > 0 else 0.0

    return contrast_value, contrast_map


def tamura_granularity(image: np.ndarray, min_size: int = 3, max_size: int = 16) -> tuple[float, list]:
    """
    Calcola la granularità Tamura di un'immagine RGB e restituisce:
      - Valore scalare della granularità
      - Dati dei granuli rilevati (coordinate e dimensioni)

    Args:
        image (np.ndarray): Immagine RGB (HxWx3), PNG.
        min_size (int): Dimensione minima dei granuli (pixel).
        max_size (int): Dimensione massima dei granuli (pixel).

    Returns:
        granularity_value (float): Valore scalare della granularità Tamura.
        granules_data (list): Lista di tuple (x, y, area) per ogni granulo rilevato.
    """

    # Step 1: Converti in scala di grigi (math esplicita)
    # Y = 0.299*R + 0.587*G + 0.114*B
    Y = (0.299 * image[..., 0] + 0.587 * image[..., 1] + 0.114 * image[..., 2]).astype(np.float32)

    # Step 2: Applica filtro Laplaciano (math esplicita)
    # Laplaciano evidenzia le variazioni locali (granuli)
    kernel = np.array([[0, 1, 0],
                       [1, -4, 1],
                       [0, 1, 0]], dtype=np.float32)
    lap = cv2.filter2D(Y, -1, kernel)

    # Step 3: Soglia per isolare le regioni granulari (math esplicita)
    # Soglia semplice: granuli = |lap| > threshold
    threshold = np.percentile(np.abs(lap), 95)  # soglia robusta, solo picchi
    binary_map = (np.abs(lap) > threshold).astype(np.uint8)

    # Step 4: Labeling con connected components (basso livello)
    # Ogni granulo è una componente connessa
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_map, connectivity=8)

    # Step 5: Filtra i granuli per area (basso livello)
    granules_data = []
    for i in range(1, num_labels):  # Salta lo sfondo (label 0)
        area = stats[i, cv2.CC_STAT_AREA]
        if min_size ** 2 <= area <= max_size ** 2:
            x, y = centroids[i]
            granules_data.append((int(x), int(y), int(area)))

    # Step 6: Calcola la granularità Tamura come densità di granuli
    granularity_value = len(granules_data) / (image.shape[0] * image.shape[1])

    return granularity_value, granules_data
