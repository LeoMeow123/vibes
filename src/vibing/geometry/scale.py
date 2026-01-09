"""
Pixel to real-world unit conversion.

Convert pixel measurements to real-world units (cm, mm, etc.) using
a known reference distance in the image.
"""

from dataclasses import dataclass
from typing import Union
import numpy as np
from numpy.typing import ArrayLike


@dataclass
class PixelScale:
    """
    Pixel-to-real-world scale converter.

    Create from a known reference measurement, then use to convert
    any pixel values to real-world units.

    Attributes:
        px_per_unit: Pixels per real-world unit (e.g., pixels per cm)
        unit: Name of the real-world unit (default: "cm")

    Example:
        >>> # A 10cm ruler spans 500 pixels in the image
        >>> scale = PixelScale.from_reference(pixels=500, real_distance=10, unit="cm")
        >>> scale.to_real(100)  # 100 pixels = ?
        2.0
        >>> scale.to_pixels(5)  # 5 cm = ?
        250.0
    """

    px_per_unit: float
    unit: str = "cm"

    @classmethod
    def from_reference(
        cls,
        pixels: float,
        real_distance: float,
        unit: str = "cm",
    ) -> "PixelScale":
        """
        Create scale from a known reference measurement.

        Args:
            pixels: Distance in pixels of the reference object
            real_distance: Actual distance of the reference object
            unit: Unit of the real distance (default: "cm")

        Returns:
            PixelScale object for conversions

        Example:
            >>> # A ruler shows 20cm spanning 1000 pixels
            >>> scale = PixelScale.from_reference(pixels=1000, real_distance=20, unit="cm")
            >>> scale.px_per_unit
            50.0
        """
        if real_distance <= 0:
            raise ValueError("real_distance must be positive")
        if pixels <= 0:
            raise ValueError("pixels must be positive")

        return cls(px_per_unit=pixels / real_distance, unit=unit)

    @classmethod
    def from_two_points(
        cls,
        point1: tuple[float, float],
        point2: tuple[float, float],
        real_distance: float,
        unit: str = "cm",
    ) -> "PixelScale":
        """
        Create scale from two points with known real-world distance.

        Args:
            point1: (x, y) coordinates of first point in pixels
            point2: (x, y) coordinates of second point in pixels
            real_distance: Actual distance between points
            unit: Unit of the real distance (default: "cm")

        Returns:
            PixelScale object for conversions

        Example:
            >>> # Two markers 15cm apart are at these pixel coordinates
            >>> scale = PixelScale.from_two_points((100, 200), (400, 600), real_distance=15)
            >>> scale.to_real(50)  # Convert 50 pixels
            1.5
        """
        p1 = np.asarray(point1, dtype=np.float64)
        p2 = np.asarray(point2, dtype=np.float64)
        pixel_distance = float(np.linalg.norm(p2 - p1))

        return cls.from_reference(pixel_distance, real_distance, unit)

    def to_real(self, pixels: Union[float, ArrayLike]) -> Union[float, np.ndarray]:
        """
        Convert pixel distance to real-world units.

        Args:
            pixels: Distance(s) in pixels (scalar or array)

        Returns:
            Distance(s) in real-world units

        Example:
            >>> scale = PixelScale(px_per_unit=50, unit="cm")
            >>> scale.to_real(100)
            2.0
            >>> scale.to_real([50, 100, 150])
            array([1., 2., 3.])
        """
        arr = np.asarray(pixels, dtype=np.float64)
        result = arr / self.px_per_unit

        if result.ndim == 0:
            return float(result)
        return result

    def to_pixels(self, real: Union[float, ArrayLike]) -> Union[float, np.ndarray]:
        """
        Convert real-world distance to pixels.

        Args:
            real: Distance(s) in real-world units (scalar or array)

        Returns:
            Distance(s) in pixels

        Example:
            >>> scale = PixelScale(px_per_unit=50, unit="cm")
            >>> scale.to_pixels(2)
            100.0
        """
        arr = np.asarray(real, dtype=np.float64)
        result = arr * self.px_per_unit

        if result.ndim == 0:
            return float(result)
        return result

    def to_real_area(self, pixels_squared: Union[float, ArrayLike]) -> Union[float, np.ndarray]:
        """
        Convert pixel area to real-world area.

        Args:
            pixels_squared: Area(s) in pixels squared

        Returns:
            Area(s) in real-world units squared

        Example:
            >>> scale = PixelScale(px_per_unit=50, unit="cm")
            >>> scale.to_real_area(2500)  # 2500 px² = 1 cm²
            1.0
        """
        arr = np.asarray(pixels_squared, dtype=np.float64)
        result = arr / (self.px_per_unit ** 2)

        if result.ndim == 0:
            return float(result)
        return result

    def __repr__(self) -> str:
        return f"PixelScale({self.px_per_unit:.2f} px/{self.unit})"


def px_to_real(
    pixels: Union[float, ArrayLike],
    reference_pixels: float,
    reference_distance: float,
) -> Union[float, np.ndarray]:
    """
    Quick conversion from pixels to real-world units.

    Convenience function when you don't need to reuse the scale.

    Args:
        pixels: Value(s) to convert
        reference_pixels: Known reference distance in pixels
        reference_distance: Known reference distance in real units

    Returns:
        Converted value(s) in real-world units

    Example:
        >>> # A 10cm ruler is 500px, convert 250px to cm
        >>> px_to_real(250, reference_pixels=500, reference_distance=10)
        5.0
    """
    scale = PixelScale.from_reference(reference_pixels, reference_distance)
    return scale.to_real(pixels)


def compute_scale(
    point1: tuple[float, float],
    point2: tuple[float, float],
    real_distance: float,
    unit: str = "cm",
) -> PixelScale:
    """
    Compute pixel scale from two reference points.

    Alias for PixelScale.from_two_points() for convenience.

    Args:
        point1: (x, y) of first reference point in pixels
        point2: (x, y) of second reference point in pixels
        real_distance: Known distance between points
        unit: Unit name (default: "cm")

    Returns:
        PixelScale object

    Example:
        >>> scale = compute_scale((0, 0), (100, 0), real_distance=5, unit="cm")
        >>> scale.to_real(50)
        2.5
    """
    return PixelScale.from_two_points(point1, point2, real_distance, unit)
