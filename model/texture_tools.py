# ========================================================
# 0. TABELLA DELLE FIRME DELLE FUNZIONI IN QUESTO FILE
#
# compute_directionality_grid(img: np.ndarray) -> tuple[float, np.ndarray]
#     # Calcola la direzionalità Tamura e restituisce valore scalare + istogramma angolare.
#
# tamura_contrast_map(image: np.ndarray) -> tuple[float, np.ndarray]
#     # Calcola il contrasto Tamura e restituisce valore scalare + mappa locale.
#
# tamura_granularity(image: np.ndarray, min_size: int = 3, max_size: int = 16) -> tuple[float, list]
#     # Calcola la granularità Tamura e restituisce valore scalare + lista dei granuli.
# ========================================================

# ========================================================
# 1. IMPORT NECESSARI
import cv2
import numpy as np
from model import color_tools
# ========================================================

# ========================================================
# 2. DIREZIONALITÀ TAMURA
def compute_directionality_grid(
        img: np.ndarray,
) -> tuple[float, np.ndarray]:
    """
    Calcola la direzionalità di Tamura per una immagine (array numpy).
    Utilizza la componente Y di YCbCr come intensità luminosa.
    """
    #fissi
    bin_width_deg: int = 10
    grid_step: int = 8

    # RGB -> YCbCr, usa la componente Y come grigia
    ycbcr_img = color_tools.convert_rgb_to_ycbcr(img)
    img_gray = ycbcr_img[..., 0]

    # Campionamento griglia, per velocizzare (slicing)
    img_sampled = img_gray[::grid_step, ::grid_step]
    h, w = img_sampled.shape

    # Kernel Sobel
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=float)
    ky = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]], dtype=float)

    gx = np.zeros((h, w), dtype=float)
    gy = np.zeros((h, w), dtype=float)
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            region = img_sampled[i - 1:i + 2, j - 1:j + 2]
            gx[i, j] = np.sum(region * kx)
            gy[i, j] = np.sum(region * ky)


    """
    spiegazione: 
    Si creano due matrici (kx e ky) che rappresentano i filtri Sobel,  
    rispettivamente per la direzione orizzontale e verticale.
    
    Si preparano due array vuoti (gx e gy), della stessa dimension dell’immagine, 
    per contenere i risultati delle convoluzioni.

    Si analizza ogni pixel interno dell’immagine, escludendo i bordi per evitare errori di calcolo.

    Per ogni pixel, si seleziona una finestra 3x3 centrata sul pixel di interesse.

    Applicazione convoluzione:
    Si moltiplica la regione locale per il kernel Sobel orizzontale (kx) e si somma il risultato, ottenendo il valore gx.
    Si ripete la stessa operazione con il kernel verticale (ky) per ottenere gy.
    """

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
# ========================================================

# ========================================================
# 3. CONTRASTO TAMURA
def tamura_contrast_map(image: np.ndarray) -> tuple[float, np.ndarray]:
    """
    Calcola il valore Tamura per il contrasto e genera la mappa di contrasto locale per un'immagine RGB.
    Lo slicing usa passo 8 sia orizzontale che verticale.
    """
    ycbcr_img = color_tools.convert_rgb_to_ycbcr(image)
    Y = ycbcr_img[..., 0]
    win_size = 7
    pad = win_size // 2

    Y_pad = np.pad(Y, pad, mode='reflect')
    H, W = Y.shape
    contrast_map = np.zeros((H, W), dtype=np.float32)
    step = 8

    for i in range(0, H, step):
        for j in range(0, W, step):
            i0 = i
            j0 = j
            patch = Y_pad[i0:i0 + win_size, j0:j0 + win_size]
            mu = np.mean(patch)
            sigma = np.std(patch)
            mean_abs = np.mean(np.abs(patch - mu))
            local_contrast = sigma / (mean_abs ** 0.25) if mean_abs > 0 else 0.0
            contrast_map[i0:i0 + step, j0:j0 + step] = local_contrast

    """spiegazione:
       L’immagine viene analizzata a blocchi di dimensione 8x8: per ogni posizione, 
       si estrae una patch locale 7x7 dalla luminanza (Y_pad) centrata sui pixel di interesse.
       Per ciascuna patch si calcolano:
       la media (mu),
       la deviazione standard (sigma),
       il valore assoluto medio rispetto alla media (mean_abs).
       Il contrasto locale viene calcolato secondo la formula di Tamura:
       local_contrast = sigma / (mean_abs ** 0.25)
       se il valore assoluto medio è positivo, altrimenti si assegna zero.
       Il valore così ottenuto viene assegnato all’intera regione 8x8 della contrast_map."""

    mu_global = np.mean(Y)
    sigma_global = np.std(Y)
    mean_abs_global = np.mean(np.abs(Y - mu_global))
    contrast_value = sigma_global / (mean_abs_global ** 0.25) if mean_abs_global > 0 else 0.0

    return contrast_value, contrast_map
# ========================================================

# ========================================================
# 4. GRANULARITÀ TAMURA
def tamura_granularity(image: np.ndarray, min_size: int = 3, max_size: int = 16) -> tuple[float, list]:
    """
    Calcola la granularità Tamura di un'immagine RGB e restituisce:
      - Valore scalare della granularità
      - Dati dei granuli rilevati (coordinate e dimensioni)
    """
    Y = (0.299 * image[..., 0] + 0.587 * image[..., 1] + 0.114 * image[..., 2]).astype(np.float32)

    kernel = np.array([[0, 1, 0],
                       [1, -4, 1],
                       [0, 1, 0]], dtype=np.float32)
    lap = cv2.filter2D(Y, -1, kernel)
    """Si applica un filtro Laplaciano alla matrice di luminanza Y. Il kernel Laplaciano evidenzia le variazioni rapide 
    di intensità, cioè i bordi e le strutture granulari dell’immagine. Il risultato (lap) è una nuova matrice che mette 
    in risalto le zone con cambiamenti bruschi di luminanza."""

    threshold = np.percentile(np.abs(lap), 95)
    binary_map = (np.abs(lap) > threshold).astype(np.uint8)
    """Si calcola la soglia come il 95° percentile del valore assoluto di lap, selezionando solo le variazioni più intense.
     Si crea una mappa binaria (binary_map) in cui i pixel con variazione superiore alla soglia vengono impostati a 1 (o 255),
      gli altri a 0. Questo passaggio isola le strutture granulari più evidenti."""

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_map, connectivity=8)
    """Si usa la funzione cv2.connectedComponentsWithStats per identificare tutte le regioni connesse (granuli) nella mappa 
    binaria. Questa funzione restituisce:
    il numero totale di regioni trovate,
    una mappa di etichette per ogni pixel,
    le statistiche (area, bounding box) di ciascuna regione,
    le coordinate dei centroidi."""

    granules_data = []
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if min_size ** 2 <= area <= max_size ** 2:
            x, y = centroids[i]
            granules_data.append((int(x), int(y), int(area)))

    """Si scorre la lista delle regioni connesse, ignorando lo sfondo. Per ogni regione, si controlla che 
    la sua area sia compresa tra min_size^2 e max_size^2. Se la regione soddisfa il criterio, si registra 
    il suo centroide (x, y) e la sua area, aggiungendoli alla lista dei granuli rilevati."""

    granularity_value = len(granules_data) / (image.shape[0] * image.shape[1])

    return granularity_value, granules_data

# ========================================================
