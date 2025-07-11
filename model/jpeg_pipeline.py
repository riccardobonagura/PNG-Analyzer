import numpy as np
from .color_tools import convert_rgb_to_ycbcr, split_ycbcr_channels
from .subsampling_tools import subsample_420
from .jpeg_tools import jpeg_encode_channel, STD_LUMA_QUANT_TABLE, STD_CHROMA_QUANT_TABLE, export_jpeg_bytes_from_blocks
from .jpeg_tools import pad_to_block_size

def jpeg_encode_image(rgb_image: np.ndarray):
    """
    Complete JPEG encoding pipeline (without entropy encoding).
    Args:
        rgb_image: np.ndarray of shape (H, W, 3), dtype uint8
    Returns:
        Dictionary with quantized DCT blocks for Y, Cb, Cr
    """
    # 0. PADDING
    rgb_image = pad_to_block_size(rgb_image, 8)

    # 1. RGB to YCbCr
    ycbcr = convert_rgb_to_ycbcr(rgb_image)

    # 2. 4:2:0 subsampling
    ycbcr_420 = subsample_420(ycbcr)

    # 3. Split channels
    Y, Cb, Cr = split_ycbcr_channels (ycbcr_420)


    # 4. JPEG encoding steps for each channel
    Y_blocks = jpeg_encode_channel(Y, STD_LUMA_QUANT_TABLE)
    Cb_blocks = jpeg_encode_channel(Cb, STD_CHROMA_QUANT_TABLE)
    Cr_blocks = jpeg_encode_channel(Cr, STD_CHROMA_QUANT_TABLE)

    # 5. Return results as a dictionary
    jpeg_data = {
        "Y_blocks": Y_blocks,
        "Cb_blocks": Cb_blocks,
        "Cr_blocks": Cr_blocks,
        # Optionally: additional metadata (e.g., original shape)
    }

    tables = [STD_LUMA_QUANT_TABLE, STD_CHROMA_QUANT_TABLE]

    jpeg_bytes = export_jpeg_bytes_from_blocks(jpeg_data, tables)


    return jpeg_data