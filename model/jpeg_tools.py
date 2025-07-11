# ========================================================
# 0. TABELLA DELLE FIRME DELLE FUNZIONI IN QUESTO FILE
#
# pad_to_block_size(img: np.ndarray, block_size: int = 8) -> np.ndarray
#     # Aggiunge padding all'immagine per renderla multipla di block_size.
#
# split_into_blocks(channel: np.ndarray, block_size: int = 8) -> np.ndarray
#     # Suddivide la matrice canale in blocchi non sovrapposti.
#
# dct_2d(block: np.ndarray) -> np.ndarray
#     # Applica la DCT 2D ortogonale a un blocco.
#
# apply_dct_to_blocks(blocks: np.ndarray) -> np.ndarray
#     # Applica la DCT 2D a tutti i blocchi di un array 4D.
#
# quantize_block(block: np.ndarray, quant_tbl: np.ndarray) -> np.ndarray
#     # Quantizza un blocco usando la tabella fornita.
#
# dequantize_block(block: np.ndarray, quant_tbl: np.ndarray) -> np.ndarray
#     # Dequantizza un blocco usando la tabella fornita.
#
# get_quant_tables(level: str) -> Tuple[np.ndarray, np.ndarray]
#     # Restituisce la coppia di tabelle di quantizzazione per il livello richiesto.
#
# zigzag_order(block: np.ndarray) -> np.ndarray
#     # Ordina un blocco 8x8 secondo lo schema zigzag standard JPEG.
#
# entropy_encode(blocks: np.ndarray) -> np.ndarray
#     # Stub: dovrebbe implementare la codifica entropica (non implementata).
#
# jpeg_encode_channel(channel: np.ndarray, quant_table: np.ndarray) -> np.ndarray
#     # Pipeline didattica per un singolo canale JPEG: blocchi, DCT, quantizzazione.
#
# blocks_to_image(blocks: np.ndarray) -> np.ndarray
#     # Ricompone la matrice immagine dai blocchi (utile per coefficienti).
#
# export_jpeg_bytes_from_blocks(jpeg_data: dict, quant_tables: Optional[List[np.ndarray]]) -> bytes
#     # Esporta i blocchi quantizzati come file JPEG e restituisce i bytes.
# ========================================================

# ========================================================
# 1. IMPORT NECESSARI
import numpy as np
# ========================================================

# ========================================================
# 2. PADDING DELL'IMMAGINE
# Funzione che aggiunge padding a una immagine per renderla multipla di block_size (default 8).
def pad_to_block_size(img, block_size=8):
    # Ottengo dimensioni originali
    h, w = img.shape[:2]
    # Calcolo necessità di padding
    pad_h = (block_size - h % block_size) % block_size
    pad_w = (block_size - w % block_size) % block_size
    # Se non serve padding, restituisco l'immagine originale
    if pad_h == 0 and pad_w == 0:
        return img
    # Applico padding: diverso per immagini grayscale o RGB
    if img.ndim == 2:
        return np.pad(img, ((0, pad_h), (0, pad_w)), mode='edge')
    else:
        return np.pad(img, ((0, pad_h), (0, pad_w), (0, 0)), mode='edge')
# ========================================================

# ========================================================
# 3. SUDDIVISIONE IN BLOCCHI
# Funzione che divide una matrice canale in blocchi non sovrapposti di block_size x block_size.
def split_into_blocks(channel: np.ndarray, block_size: int = 8):
    # Ottengo dimensioni
    h, w = channel.shape
    # Controllo che siano multipli di block_size
    assert h % block_size == 0 and w % block_size == 0, "La dimensione dell'immagine deve essere multipla del block size."
    # Reshape e trasposizione per ottenere array 4D di blocchi
    return (channel
            .reshape(h // block_size, block_size, w // block_size, block_size)
            .transpose(0, 2, 1, 3))
# ========================================================

# ========================================================
# 4. TRASFORMATA DCT
# Funzione che applica la DCT 2D (tipo II) a un blocco 8x8.
def dct_2d(block: np.ndarray):
    # Importo la funzione DCT quando serve (scelta didattica per mostrare dipendenza locale)
    from scipy.fftpack import dct
    # Applico la DCT prima per colonne, poi per righe
    return dct(dct(block.T, norm='ortho').T, norm='ortho')

# Funzione che applica la DCT su tutti i blocchi di un array 4D
def apply_dct_to_blocks(blocks: np.ndarray):
    # Creo array vuoto per i risultati
    dct_blocks = np.empty_like(blocks, dtype=np.float32)
    # Itero su tutti gli indici dei blocchi
    it = np.nditer(blocks[..., 0, 0], flags=['multi_index'])
    for _ in it:
        i, j = it.multi_index
        # Applico la DCT 2D su ogni blocco e salvo il risultato
        dct_blocks[i, j] = dct_2d(blocks[i, j])
    return dct_blocks
# ========================================================

# ========================================================
# 5. QUANTIZZAZIONE
# Funzione che quantizza un blocco usando una tabella di quantizzazione
def quantize_block(block: np.ndarray, quant_tbl: np.ndarray):
    # Divisione elemento per elemento e arrotondamento
    return np.round(block / quant_tbl).astype(np.int32)

# Funzione che dequantizza un blocco usando una tabella di quantizzazione
def dequantize_block(block: np.ndarray, quant_tbl: np.ndarray):
    # Moltiplicazione elemento per elemento
    return (block * quant_tbl).astype(np.float32)
# ========================================================

# ========================================================
# 6. TABELLE DI QUANTIZZAZIONE STANDARD
# Diverse tabelle predefinite per la compressione JPEG a vari livelli

LUMA_QUANT_TABLE_LOW = np.array([
    [8, 6, 5, 8,12,20,26,31],
    [6, 6, 7,10,13,29,30,28],
    [7, 7, 8,12,20,29,35,28],
    [7, 9,11,14,26,44,40,32],
    [9,11,19,28,34,55,52,39],
    [12,18,28,32,41,52,57,46],
    [25,32,39,44,52,61,60,50],
    [36,46,48,49,56,50,52,50]
], dtype=np.float32)

CHROMA_QUANT_TABLE_LOW = np.array([
    [9, 9,12,23,48,48,48,48],
    [9,11,13,32,48,48,48,48],
    [12,13,28,48,48,48,48,48],
    [23,32,48,48,48,48,48,48],
    [48,48,48,48,48,48,48,48],
    [48,48,48,48,48,48,48,48],
    [48,48,48,48,48,48,48,48],
    [48,48,48,48,48,48,48,48]
], dtype=np.float32)

LUMA_QUANT_TABLE_MED = np.array([
    [16,11,10,16,24,40,51,61],
    [12,12,14,19,26,58,60,55],
    [14,13,16,24,40,57,69,56],
    [14,17,22,29,51,87,80,62],
    [18,22,37,56,68,109,103,77],
    [24,35,55,64,81,104,113,92],
    [49,64,78,87,103,121,120,101],
    [72,92,95,98,112,100,103,99]
], dtype=np.float32)

CHROMA_QUANT_TABLE_MED = np.array([
    [17,18,24,47,99,99,99,99],
    [18,21,26,66,99,99,99,99],
    [24,26,56,99,99,99,99,99],
    [47,66,99,99,99,99,99,99],
    [99,99,99,99,99,99,99,99],
    [99,99,99,99,99,99,99,99],
    [99,99,99,99,99,99,99,99],
    [99,99,99,99,99,99,99,99]
], dtype=np.float32)

LUMA_QUANT_TABLE_HIGH = np.array([
    [16,32,32,32,32,32,32,32],
    [32,32,32,32,32,32,32,32],
    [32,32,32,32,32,32,32,32],
    [32,32,32,32,32,32,32,32],
    [32,32,32,32,32,32,32,32],
    [32,32,32,32,32,32,32,32],
    [32,32,32,32,32,32,32,32],
    [32,32,32,32,32,32,32,32]
], dtype=np.float32)

CHROMA_QUANT_TABLE_HIGH = np.full((8,8), 50, dtype=np.float32)
# ========================================================

# ========================================================
# 7. SELEZIONE TABELLE DI QUANTIZZAZIONE
# Funzione che restituisce le tabelle di quantizzazione in base al livello richiesto.
def get_quant_tables(level):
    # Livello "low" = compressione bassa, qualità alta
    if level == "low":
        return LUMA_QUANT_TABLE_LOW, CHROMA_QUANT_TABLE_LOW
    # Livello "high" = compressione alta, qualità bassa
    elif level == "high":
        return LUMA_QUANT_TABLE_HIGH, CHROMA_QUANT_TABLE_HIGH
    # Default: livello medio
    else:
        return LUMA_QUANT_TABLE_MED, CHROMA_QUANT_TABLE_MED
# ========================================================

# ========================================================
# 8. ORDINAMENTO ZIGZAG
# Funzione che trasforma una matrice 8x8 in un vettore secondo l'ordine zigzag JPEG.
def zigzag_order(block: np.ndarray):
    # Indici zigzag secondo lo standard JPEG
    zigzag_indices = [
        (0,0),(0,1),(1,0),(2,0),(1,1),(0,2),(0,3),(1,2),
        (2,1),(3,0),(4,0),(3,1),(2,2),(1,3),(0,4),(0,5),
        (1,4),(2,3),(3,2),(4,1),(5,0),(6,0),(5,1),(4,2),
        (3,3),(2,4),(1,5),(0,6),(0,7),(1,6),(2,5),(3,4),
        (4,3),(5,2),(6,1),(7,0),(7,1),(6,2),(5,3),(4,4),
        (3,5),(2,6),(1,7),(2,7),(3,6),(4,5),(5,4),(6,3),
        (7,2),(7,3),(6,4),(5,5),(4,6),(3,7),(4,7),(5,6),
        (6,5),(7,4),(7,5),(6,6),(5,7),(6,7),(7,6),(7,7)
    ]
    # Creo un array 1D dei valori ordinati zigzag
    return np.array([block[i,j] for i,j in zigzag_indices])
# ========================================================

# ========================================================
# 9. ENTROPY CODING (STUB)
# Funzione stub per la codifica entropica (non implementata).
def entropy_encode(blocks):
    # Qui si dovrebbe implementare la codifica entropica (es. Huffman)
    return blocks
# ========================================================

# ========================================================
# 10. PIPELINE SINGOLO CANALE JPEG
# Funzione che esegue la pipeline JPEG su un singolo canale (Y, Cb o Cr).
def jpeg_encode_channel(channel, quant_table):
    """
    Pipeline completa per un singolo canale:
    - Suddivisione in blocchi
    - Shift di 128 (centro attorno a zero per la DCT)
    - Applicazione DCT
    - Quantizzazione
    Restituisce blocchi quantizzati.
    """
    # Conversione a float e shift
    channel = channel.astype(np.float32) - 128
    # Suddivido in blocchi 8x8
    blocks = split_into_blocks(channel)
    # Applico la DCT a ogni blocco
    dct_blocks = apply_dct_to_blocks(blocks)
    # Quantizzo ogni blocco
    quant_blocks = np.empty_like(dct_blocks, dtype=np.int32)
    it = np.nditer(dct_blocks[..., 0, 0], flags=['multi_index'])
    for _ in it:
        i, j = it.multi_index
        quant_blocks[i, j] = quantize_block(dct_blocks[i, j], quant_table)
    return quant_blocks
# ========================================================

# ========================================================
# 11. RICOSTRUZIONE MATRICE DA BLOCCHI
# Funzione che ricompone la matrice immagine dai blocchi (utile per coefficienti).
def blocks_to_image(blocks):
    # Ottengo dimensioni
    num_blocchi_y, num_blocchi_x, block_h, block_w = blocks.shape
    # Trasformo e ridispongo per ottenere la matrice originale
    return blocks.transpose(0,2,1,3).reshape(num_blocchi_y*block_h, num_blocchi_x*block_w)
# ========================================================

# ========================================================
# 12. ESPORTAZIONE JPEG
# Import necessari per la sezione export
import jpegio as jio
from PIL import Image
import tempfile
import os

# Funzione per esportare i blocchi quantizzati come file JPEG e restituire i bytes.
def export_jpeg_bytes_from_blocks(jpeg_data, quant_tables=None):
    """
    Crea un file JPEG, partendo da blocchi quantizzati jpeg_data, e restituisce i bytes.
    Args:
        jpeg_data: dict con chiavi 'Y_blocks', 'Cb_blocks', 'Cr_blocks' (già quantizzati)
        quant_tables: lista di 2 numpy array per Y e Cb/Cr
    Returns:
        jpeg_bytes: bytes del file JPEG
    """
    # Estraggo i blocchi
    Y_blocks = jpeg_data["Y_blocks"]
    Cb_blocks = jpeg_data["Cb_blocks"]
    Cr_blocks = jpeg_data["Cr_blocks"]
    n_blocks_y, n_blocks_x, block_size, _ = Y_blocks.shape
    # Calcolo dimensione immagine
    H, W = n_blocks_y * block_size, n_blocks_x * block_size

    # Creo directory temporanea per il file JPEG
    with tempfile.TemporaryDirectory() as tmpdir:
        dummy_path = os.path.join(tmpdir, "dummy.jpg")
        output_path = os.path.join(tmpdir, "output.jpg")
        # Creo immagine dummy RGB per inizializzare
        dummy = Image.new("RGB", (W, H), color=(128,128,128))
        dummy.save(dummy_path, "JPEG")

        # Leggo oggetto JPEG con jpegio
        jpeg = jio.read(dummy_path)
        # Sostituisco i coefficienti con i blocchi passati
        jpeg.coef_arrays[0][:] = blocks_to_image(Y_blocks)
        jpeg.coef_arrays[1][:] = blocks_to_image(Cb_blocks)
        jpeg.coef_arrays[2][:] = blocks_to_image(Cr_blocks)

        # Debug: possibilità di salvare i coefficienti come immagini
        # imageio.imwrite("debug_Cb_coeff.png", blocks_to_image(Cb_blocks))
        # imageio.imwrite("debug_Cr_coeff.png", blocks_to_image(Cr_blocks))

        # Sostituisco le tabelle di quantizzazione se fornite
        if quant_tables is not None:
            jpeg.quant_tables[0] = quant_tables[0]
            jpeg.quant_tables[1] = quant_tables[1]

        # Scrivo il JPEG finale
        jio.write(jpeg, output_path)

        # Leggo i bytes del file JPEG
        with open(output_path, "rb") as f:
            jpeg_bytes = f.read()
        # Rimuovo il file temporaneo se presente
        if os.path.exists(output_path):
            os.remove(output_path)

    return jpeg_bytes
# ========================================================