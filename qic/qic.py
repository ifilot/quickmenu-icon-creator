import numpy as np
from PIL import Image, ImageDraw

class QIC:
    """
    Quickmenu Icon Creator class
    """
    def __init__(self, palette='legacy'):
        # define EGA color scheme
        self.colors = [
            (0,0,0),
            (0,0,195),
            (0,125,0),
            (0, 170, 174),
            (166,0,0),
            (158,0,158),
            (195,93,0),
            (170,170,170),
            (117,117,117),
            (0,125,243),
            (0,255,0),
            (0,255,255),
            (255,0,77),
            (255,0,255),
            (255,255,0),
            (255,255,255)
        ]
        if palette == 'ega':
            self.colors = [
                (0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170),
                (170, 0, 0), (170, 0, 170), (170, 85, 0), (170, 170, 170),
                (85, 85, 85), (85, 85, 255), (85, 255, 85), (85, 255, 255),
                (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255)
            ]
        elif palette != 'legacy':
            raise ValueError("palette must be 'legacy' or 'ega'")

    def png2icc(self, infile, outfile, *, metric='rgb', dither=0.0):
        """
        Convert a 32x32 PNG file to an ICC file.

        metric='lab' uses perceptual color distance. dither is the fraction
        (0..1) of quantization error diffused to adjacent opaque pixels.
        Defaults preserve the original RGB conversion behavior.
        """
        print('Reading PNG file: %s' % infile)
        img, ega_array = self.__convert_png_to_icc(infile, metric, dither)
        res = self.__build_icc(ega_array)

        print('Writing ICC file: %s' % outfile)
        with open(outfile, 'wb') as f:
            f.write(res)

    def icc2png(self, infile, outfile):
        """Save a transparent 32x32 PNG using this instance's display palette."""
        self.__icc2img(self.__read_icon(infile)).save(outfile)

    def show_icc(self, infile):
        """
        Visualize an .ICC file; the icon is automatically upscaled to a
        256 x 256 image using NEAREST interpolation
        """
        print("Reading: %s" % infile)
        data = self.__read_icon(infile)
        img = self.__icc2img(data)
        large = img.resize((256,256), Image.NEAREST)
        print("Expanding icon to 256 x 256 px and visualizing result.")
        large.show()
        
    def compare_icc(self, pngfile, iccfile):
        """
        Compare a PNG file with an ICC file
        """
        print("Reading PNG: %s" % pngfile)
        imgsource = Image.open(pngfile)
        largepng = imgsource.resize((256,256), Image.NEAREST)
        
        print("Reading ICC: %s" % iccfile)
        data = self.__read_icon(iccfile)
        img = self.__icc2img(data)
        largeicc = img.resize((256,256), Image.NEAREST)
        
        comp = Image.fromarray(np.hstack((np.array(largepng),np.array(largeicc))))    
        comp.show()

    def __icc2img(self, data):
        """
        Convert a .ICC file to a PIL image
        """
        img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        pixels = img.load()
        
        for y in range(0,32):
            r = np.zeros(32, dtype=np.uint8)
            for b in range(4): # loop over bit planes
                for x in range(4):
                    c = data[y * 16 + b * 4 + x + 4]
                    r[x*8:(x+1)*8] += self.__bin_array(c, 8) * (1 << b)
            
            for x in range(32):
                rgb = self.__ega_color(r[x])
                pixels[x,y] = (rgb[0], rgb[1], rgb[2],255)
                
        for y in range(0,32):
            r = np.zeros(32, dtype=np.uint8)
            for b in range(4): # loop over bit planes
                for x in range(4):
                    c = data[y * 16 + b * 4 + x + 520]
                    r[x*8:(x+1)*8] += self.__bin_array(c, 8) * (1 << b)
            
            for x in range(32):
                p = pixels[x,y]
                p = (p[0], p[1], p[2], 255 if r[x] == 15 else 0)
                pixels[x,y] = p
        
        return img

    def __build_icc(self, ega_array):
        """
        Build an ICC file from raw image array
        """
        data = bytearray([0x1F,0,0x1F,0])
        for y in range(0,32):
            for b in range(4): # loop over bit planes
                r = np.zeros(4, dtype=np.uint8)
                for x in range(32):
                    r[x//8] |= (ega_array[x,y,0] >> b & 0x01) << (7 - x%8)
                for rr in r:
                    data.append(rr)
        
        data += bytearray([0x1F,0,0x1F,0])
        
        for y in range(0,32):
            for b in range(4): # loop over bit planes
                r = np.zeros(4, dtype=np.uint8)
                for x in range(32):
                    r[x//8] |= (ega_array[x,y,1] >> b & 0x01) << (7 - x%8)
                for rr in r:
                    data.append(rr)
        
        return data

    def __ega_color(self, ega):
        """
        Convert 4bpp EGA color to 24bpp color
        """
        conv = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15]
        
        return self.colors[conv[ega]]

    @staticmethod
    def __lab(rgb):
        """Convert sRGB to CIELAB using the D65 reference white."""
        rgb = np.asarray(rgb, dtype=np.float64) / 255.0
        linear = np.where(rgb <= 0.04045, rgb / 12.92,
                          ((rgb + 0.055) / 1.055) ** 2.4)
        xyz = linear @ np.array([
            [0.4124564, 0.2126729, 0.0193339],
            [0.3575761, 0.7151522, 0.1191920],
            [0.1804375, 0.0721750, 0.9503041]])
        xyz /= np.array([0.95047, 1.0, 1.08883])
        delta = 6 / 29
        f = np.where(xyz > delta ** 3, np.cbrt(xyz),
                     xyz / (3 * delta ** 2) + 4 / 29)
        return np.stack((116 * f[..., 1] - 16,
                         500 * (f[..., 0] - f[..., 1]),
                         200 * (f[..., 1] - f[..., 2])), axis=-1)

    def __convert_png_to_icc(self, filename, metric='rgb', dither=0.0):
        """
        Convert a .PNG file to a .ICC file, also return the raw pixel
        information of the PNG file
        """
        if metric not in ('rgb', 'lab'):
            raise ValueError("metric must be 'rgb' or 'lab'")
        if not 0 <= dither <= 1:
            raise ValueError('dither must be between 0 and 1')
        with Image.open(filename) as source:
            if source.size != (32, 32):
                raise ValueError('ICC icons must be exactly 32x32 pixels')
            original = source.convert('RGBA')
        pixels_source = original.load()
        
        img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        pixels_target = img.load()
        
        carr = np.array(self.colors, dtype=np.float64)
        working = np.array(original, dtype=np.float64)[:, :, :3]
        opaque = np.array(original)[:, :, 3] > 100
        if metric == 'lab':
            carr = self.__lab(carr)
            working = self.__lab(working)
        
        ega_array = np.zeros((32,32,2), dtype=np.uint8)
        
        conv = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15]
        
        for y in range(32):
            # Alternate scan direction to reduce directional diffusion streaks.
            step = -1 if dither and y % 2 else 1
            for x in (range(32) if step == 1 else range(31, -1, -1)):
                p = pixels_source[x,y]
                c = working[y, x]
                
                cc = np.array(carr - c, dtype=np.float64)
                tune = np.power(cc, 2)
                diff = np.sum(tune, axis=1)
                cd = np.argmin(diff)
                c = self.colors[cd]
                pixels_target[x,y] = (c[0], c[1], c[2], p[3])
                ega_array[x,y,0] = conv[cd]
                ega_array[x,y,1] = 0x0F if p[3] > 100 else 0
                if dither and opaque[y, x]:
                    error = (working[y, x] - carr[cd]) * dither
                    for dy, dx, weight in ((0, step, 7 / 16),
                                           (1, -step, 3 / 16),
                                           (1, 0, 5 / 16),
                                           (1, step, 1 / 16)):
                        yy, xx = y + dy, x + dx
                        if yy < 32 and 0 <= xx < 32 and opaque[yy, xx]:
                            working[yy, xx] += error * weight
        
        return img, ega_array

    def __bin_array(self, num, m):
        """
        Convert an 8 bit unsigned integer to a list of bit
        """
        return np.array(list(np.binary_repr(num).zfill(m))).astype(np.uint8)

    def __read_icon(self, filename):
        """
        Read an icon file from a file
        """
        f = open(filename, 'rb')
        data = bytearray(f.read())
        return data
