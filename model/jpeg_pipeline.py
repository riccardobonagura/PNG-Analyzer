# ========================================================
# 0. TABELLA DELLE FIRME DELLE FUNZIONI IN QUESTO FILE
#
# jpeg_encode_image(
#     rgb_image: np.ndarray,
#     luma_quant_table: np.ndarray,
#     chroma_quant_table: np.ndarray
# ) -> bytes
#     # Pipeline completa di codifica JPEG: conversione colore, subsampling,
#     # separazione canali, padding, codifica JPEG per ciascun canale,
#     # esportazione dei bytes JPEG. Restituisce i bytes JPEG risultanti.
# ========================================================

# ========================================================
# 1. IMPORT NECESSARI
import numpy as np

import model.color_tools as color_tools
import model.subsampling_tools as subsampling_tools
import model.jpeg_tools as jpeg_tools
# ========================================================

# ========================================================
# 2. PIPELINE DI CODIFICA JPEG COMPLETA
def jpeg_encode_image(
    rgb_image: np.ndarray,
    luma_quant_table: np.ndarray,
    chroma_quant_table: np.ndarray
) -> bytes:
    """
    Pipeline completa di codifica JPEG (senza codifica entropica).
    Args:
        rgb_image: np.ndarray di forma (H, W, 3), dtype uint8
        luma_quant_table: np.ndarray (8x8), tabella di quantizzazione per Y
        chroma_quant_table: np.ndarray (8x8), tabella di quantizzazione per Cb e Cr
    Returns:
        jpeg_bytes: bytes dell'immagine JPEG risultante
    """
    # 1. Conversione da RGB a YCbCr
    # Input: rgb_image (np.ndarray)
    # Output: ycbcr (np.ndarray)
    ycbcr = color_tools.convert_rgb_to_ycbcr(rgb_image)

    # 2. Sottocampionamento 4:2:0 sui canali cromatici
    # Input: ycbcr (np.ndarray)
    # Output: ycbcr_420 (np.ndarray)
    ycbcr_420 = subsampling_tools.subsample_420(ycbcr)


    # 3. Separazione dei tre canali Y, Cb, Cr
    # Input: ycbcr_420 (np.ndarray)
    # Output: Y, Cb, Cr (np.ndarray)
    Y, Cb, Cr = color_tools.split_ycbcr_channels(ycbcr_420)

    # 4. Sottocampionamento reale (half resolution) dei canali cromatici
    # Input: Cb, Cr (np.ndarray)
    # Output: Cb_420, Cr_420 (np.ndarray)
    Cb_420 = Cb[::2, ::2]
    Cr_420 = Cr[::2, ::2]

    # 5. Padding per tutti i canali per garantire dimensioni multiple di 8
    # Input: Y, Cb_420, Cr_420 (np.ndarray)
    # Output: Y_padded, Cb_420_padded, Cr_420_padded (np.ndarray)
    Y_padded = jpeg_tools.pad_to_block_size(Y, 8)
    Cb_420_padded = jpeg_tools.pad_to_block_size(Cb_420, 8)
    Cr_420_padded = jpeg_tools.pad_to_block_size(Cr_420, 8)

    # 6. Codifica JPEG per ciascun canale con le rispettive tabelle di quantizzazione
    # Input: Y_padded, Cb_420_padded, Cr_420_padded (np.ndarray)
    # Output: Y_blocks, Cb_blocks, Cr_blocks (np.ndarray)
    Y_blocks = jpeg_tools.jpeg_encode_channel(Y_padded, luma_quant_table)
    Cb_blocks = jpeg_tools.jpeg_encode_channel(Cb_420_padded, chroma_quant_table)
    Cr_blocks = jpeg_tools.jpeg_encode_channel(Cr_420_padded, chroma_quant_table)

    # 7. Costruzione dizionario con blocchi quantizzati per esportazione JPEG
    # Input: Y_blocks, Cb_blocks, Cr_blocks (np.ndarray)
    # Output: jpeg_data (dict)
    jpeg_data = {
        "Y_blocks": Y_blocks,
        "Cb_blocks": Cb_blocks,
        "Cr_blocks": Cr_blocks,
    }

    # 8. Preparazione delle tabelle di quantizzazione per l'esportazione
    # Input: luma_quant_table, chroma_quant_table (np.ndarray)
    # Output: tables (list)
    tables = [luma_quant_table, chroma_quant_table]

    # 9. Esportazione dei bytes JPEG tramite funzione dedicata
    # Input: jpeg_data (dict), tables (list)
    # Output: jpeg_bytes (bytes)
    jpeg_bytes = jpeg_tools.export_jpeg_bytes_from_blocks(jpeg_data, tables)

    # 10. Restituzione dei bytes JPEG risultanti
    return jpeg_bytes
# ========================================================