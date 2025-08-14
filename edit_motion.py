from PIL import Image
import os


def extract_static_image_from_motion_photo(input_path, output_path):
    """
    Extract image without motion photo
    """
    # End of Image (EOI) marker
    eoi_marker = b'\xff\xd9'

    try:
        # read file with binary mode
        with open(input_path, 'rb') as f:
            content = f.read()

        # find eoi marker from the end of file
        # this can ignore other eoi markers included in thumbnail
        eoi_position = content.rfind(eoi_marker)

        if eoi_position == -1:
            print("No EOI marker found in the file.")
            return

        # Image data : the position of eoi marker + the length of marker(2 bytes)
        static_image_data = content[:eoi_position + 2]

        # export image data as a new file
        with open(output_path, 'wb') as f_out:
            f_out.write(static_image_data)

        print("Saved static image to:", output_path)

    except FileNotFoundError:
        print(f"File not found: {input_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


# Usage
if __name__ == "__main__":
    # specify in/out file name
    input_file = r"D:\share\receipts\PXL_20250811_023158298_MP.jpg"
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_static{ext}"

    if os.path.exists(input_file):
        extract_static_image_from_motion_photo(input_file, output_file)

        # check if output file can be read by pillow
        try:
            with Image.open(output_file) as img:
                # image size
                print(f"Extracted image dimensions: {img.size[0]} x {img.size[1]} pixels")
                # file size(MB)
                img_file_size = os.path.getsize(output_file) / (1024 * 1024)
                print(f"Extracted image file size: {img_file_size:.2f} MB")

        except Exception as e:
            print(f"An error occurred while reading the output file: {e}")

    else:
        print(f"Input file does not exist: {input_file}")
