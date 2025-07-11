"""
DCT esplicita, non utilizzata nella versione finale perchè molto molto lenta
def dct2_manual(block):
    N = block.shape[0]
    result = np.zeros_like(block, dtype=np.float32)
    for u in range(N):
        for v in range(N):
            sum_ = 0
            for x in range(N):
                for y in range(N):
                    sum_ += block[x, y] * \
                        np.cos((2*x+1)*u*np.pi/(2*N)) * \
                        np.cos((2*y+1)*v*np.pi/(2*N))
            alpha_u = np.sqrt(1/N) if u == 0 else np.sqrt(2/N)
            alpha_v = np.sqrt(1/N) if v == 0 else np.sqrt(2/N)
            result[u, v] = alpha_u * alpha_v * sum_
    return result
"""

"""
JPEG encoding tools: DCT, quantization, block splitting, etc.
"""

import numpy as np

# 0. PADDING

def pad_to_block_size(img, block_size=8):
    h, w = img.shape[:2]
    pad_h = (block_size - h % block_size) % block_size
    pad_w = (block_size - w % block_size) % block_size
    if pad_h == 0 and pad_w == 0:
        return img
    if img.ndim == 2:
        return np.pad(img, ((0, pad_h), (0, pad_w)), mode='edge')
    else:  # RGB or YCbCr (3 channels)
        return np.pad(img, ((0, pad_h), (0, pad_w), (0, 0)), mode='edge')


# 1. 8x8 BLOCK SPLITTING
def split_into_blocks(channel: np.ndarray, block_size: int = 8):
    """
    Splits a 2D image channel into non-overlapping block_size x block_size blocks.
    Returns a 4D array: (num_blocks_y, num_blocks_x, block_size, block_size)
    """
    h, w = channel.shape
    assert h % block_size == 0 and w % block_size == 0, "Image size must be a multiple of block size"
    return (channel
            .reshape(h // block_size, block_size, w // block_size, block_size)
            .transpose(0, 2, 1, 3))

# 2. DCT (Discrete Cosine Transform)
def dct_2d(block: np.ndarray):
    """
    Applies a 2D DCT (type II) to an 8x8 block.
    Input: block, shape (8,8), float32.
    Output: DCT coefficients, shape (8,8), float32.
    """
    from scipy.fftpack import dct
    return dct(dct(block.T, norm='ortho').T, norm='ortho')

def apply_dct_to_blocks(blocks: np.ndarray):
    """
    Applies DCT to all blocks in a 4D array.
    """
    dct_blocks = np.empty_like(blocks, dtype=np.float32)
    it = np.nditer(blocks[..., 0, 0], flags=['multi_index'])
    for _ in it:
        i, j = it.multi_index
        dct_blocks[i, j] = dct_2d(blocks[i, j])
    return dct_blocks

# 3. QUANTIZATION
def quantize_block(block: np.ndarray, quant_tbl: np.ndarray):
    """
    Quantizes an 8x8 block using the provided quantization table.
    """
    return np.round(block / quant_tbl).astype(np.int32)

def dequantize_block(block: np.ndarray, quant_tbl: np.ndarray):
    """
    Dequantizes an 8x8 block using the provided quantization table.
    """
    return (block * quant_tbl).astype(np.float32)

# 4. STANDARD QUANTIZATION TABLES
STD_LUMA_QUANT_TABLE = np.array([
    [16,11,10,16,24,40,51,61],
    [12,12,14,19,26,58,60,55],
    [14,13,16,24,40,57,69,56],
    [14,17,22,29,51,87,80,62],
    [18,22,37,56,68,109,103,77],
    [24,35,55,64,81,104,113,92],
    [49,64,78,87,103,121,120,101],
    [72,92,95,98,112,100,103,99]
], dtype=np.float32)

STD_CHROMA_QUANT_TABLE = np.array([
    [17,18,24,47,99,99,99,99],
    [18,21,26,66,99,99,99,99],
    [24,26,56,99,99,99,99,99],
    [47,66,99,99,99,99,99,99],
    [99,99,99,99,99,99,99,99],
    [99,99,99,99,99,99,99,99],
    [99,99,99,99,99,99,99,99],
    [99,99,99,99,99,99,99,99]
], dtype=np.float32)

# 5. (Optional) ZIGZAG REORDERING
def zigzag_order(block: np.ndarray):
    """
    Converts an 8x8 block to a 1D array in zigzag order.
    """
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
    return np.array([block[i,j] for i,j in zigzag_indices])

# 6. (Optional) ENTROPY ENCODING STUB
def entropy_encode(blocks):
    """
    Placeholder for entropy encoding (e.g., Huffman).
    For now, just returns the quantized blocks as-is.
    """
    return blocks

# 7. PIPELINE FUNCTION
def jpeg_encode_channel(channel, quant_table):
    """
    Complete pipeline for a single channel:
    - Split into blocks
    - Subtract 128 (center around zero for DCT)
    - DCT
    - Quantize
    - (Optionally) Zigzag
    - (Optionally) Entropy encode
    Returns quantized blocks.
    """
    channel = channel.astype(np.float32) - 128
    blocks = split_into_blocks(channel)
    dct_blocks = apply_dct_to_blocks(blocks)
    quant_blocks = np.empty_like(dct_blocks, dtype=np.int32)
    it = np.nditer(dct_blocks[..., 0, 0], flags=['multi_index'])
    for _ in it:
        i, j = it.multi_index
        quant_blocks[i, j] = quantize_block(dct_blocks[i, j], quant_table)
    # For learning: you could now apply zigzag or entropy encoding here.
    return quant_blocks



# 8. JPEG building
import numpy as np
import jpegio as jio
from PIL import Image
import tempfile
import os

def export_jpeg_bytes_from_blocks(jpeg_data, quant_tables=None):
    """
    Crea un file JPEG, partendo da blocchi quantizzati jpeg_data, e restituisce i bytes.
    Args:
        jpeg_data: dict con chiavi 'Y_blocks', 'Cb_blocks', 'Cr_blocks' (già quantizzati)
        quant_tables: opzionale, lista di 2 numpy array per Y e Cb/Cr
    Returns:
        jpeg_bytes: bytes del file JPEG
    """
    Y_blocks = jpeg_data["Y_blocks"]
    Cb_blocks = jpeg_data["Cb_blocks"]
    Cr_blocks = jpeg_data["Cr_blocks"]
    n_blocks_y, n_blocks_x, block_size, _ = Y_blocks.shape
    H, W = n_blocks_y * block_size, n_blocks_x * block_size

    with tempfile.TemporaryDirectory() as tmpdir:
        dummy_path = os.path.join(tmpdir, "dummy.jpg")
        output_path = os.path.join(tmpdir, "output.jpg")
        dummy = Image.new("RGB", (W, H), color=(128,128,128))
        dummy.save(dummy_path, "JPEG")

        jpeg = jio.read(dummy_path)
        jpeg.coef_arrays[0][:] = Y_blocks
        jpeg.coef_arrays[1][:] = Cb_blocks
        jpeg.coef_arrays[2][:] = Cr_blocks

        if quant_tables is not None:
            jpeg.quant_tables[0] = quant_tables[0]
            jpeg.quant_tables[1] = quant_tables[1]

        jio.write(jpeg, output_path)

        # Leggi i bytes
        with open(output_path, "rb") as f:
            jpeg_bytes = f.read()

        # Delete the temporary output file before returning
        if os.path.exists(output_path):
            os.remove(output_path)

    return jpeg_bytes