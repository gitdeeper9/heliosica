"""
HELIOSICA Visualization Styles
Plotting styles and color schemes
Pure Python - defines styles only, actual plotting uses matplotlib externally
"""

class PlotStyles:
    """Plot style definitions"""
    
    # Color schemes for different storm categories
    STORM_COLORS = {
        'G0': '#00ff00',  # Green - Quiet
        'G1': '#aaff00',  # Light green - Minor
        'G2': '#ffff00',  # Yellow - Moderate
        'G3': '#ffaa00',  # Orange - Strong
        'G4': '#ff5500',  # Orange-red - Severe
        'G5': '#ff0000'   # Red - Extreme
    }
    
    # Color schemes for parameters
    PARAM_COLORS = {
        'Ey': '#ff0000',   # Red - Reconnection
        'Bz': '#0000ff',   # Blue - Magnetic field
        'P_ram': '#00aa00', # Green - Pressure
        'V0': '#aa00aa',    # Purple - Velocity
        'gamma': '#ffaa00', # Orange - Drag
        'omega': '#00aaaa', # Cyan - Angular spread
        'Tp': '#aa5500',    # Brown - Temperature
        'Fd': '#ff00ff',    # Magenta - Forbush
        'Kp': '#000000'     # Black - Kp index
    }
    
    # Color maps for continuous data
    TEMPERATURE_CMAP = [
        '#0000ff', '#0066ff', '#00ccff', '#66ffcc',
        '#ccff66', '#ffcc00', '#ff6600', '#ff0000'
    ]
    
    PRESSURE_CMAP = [
        '#ffffff', '#ccffff', '#99ccff', '#6699ff',
        '#3366ff', '#0033cc', '#000099', '#000066'
    ]
    
    VELOCITY_CMAP = [
        '#000000', '#330066', '#6600cc', '#9900ff',
        '#cc66ff', '#ff99cc', '#ffccff', '#ffffff'
    ]
    
    # Line styles
    LINE_STYLES = ['-', '--', '-.', ':']
    
    # Marker styles
    MARKER_STYLES = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']
    
    @classmethod
    def get_storm_color(cls, category):
        """Get color for storm category"""
        return cls.STORM_COLORS.get(category, '#888888')
    
    @classmethod
    def get_param_color(cls, param):
        """Get color for parameter"""
        return cls.PARAM_COLORS.get(param, '#888888')
    
    @classmethod
    def get_cmap(cls, name, steps=256):
        """Get color map as list of RGB tuples"""
        if name == 'temperature':
            base = cls.TEMPERATURE_CMAP
        elif name == 'pressure':
            base = cls.PRESSURE_CMAP
        elif name == 'velocity':
            base = cls.VELOCITY_CMAP
        else:
            base = ['#000000', '#ffffff']
        
        # Interpolate to requested steps
        return cls._interpolate_cmap(base, steps)
    
    @staticmethod
    def _interpolate_cmap(colors, steps):
        """Interpolate between colors"""
        if len(colors) == 1:
            return [colors[0]] * steps
        
        result = []
        n_segments = len(colors) - 1
        steps_per_segment = steps // n_segments
        
        for i in range(n_segments):
            c1 = colors[i]
            c2 = colors[i + 1]
            
            # Convert hex to RGB
            r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
            r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
            
            for j in range(steps_per_segment):
                t = j / steps_per_segment
                r = int(r1 + (r2 - r1) * t)
                g = int(g1 + (g2 - g1) * t)
                b = int(b1 + (b2 - b1) * t)
                result.append(f'#{r:02x}{g:02x}{b:02x}')
        
        return result


class PlotLayouts:
    """Plot layout definitions"""
    
    # Figure sizes (width, height in inches)
    FIGURE_SIZES = {
        'small': (6, 4),
        'medium': (8, 6),
        'large': (12, 8),
        'wide': (14, 6),
        'square': (8, 8),
        'poster': (16, 12)
    }
    
    # Font sizes
    FONT_SIZES = {
        'title': 16,
        'subtitle': 14,
        'axis_label': 12,
        'tick_label': 10,
        'legend': 10,
        'annotation': 8
    }
    
    # DPI for different outputs
    DPI = {
        'screen': 100,
        'print': 300,
        'publication': 600
    }
    
    @classmethod
    def get_figure_size(cls, name):
        """Get figure size by name"""
        return cls.FIGURE_SIZES.get(name, (8, 6))
    
    @classmethod
    def get_font_size(cls, name):
        """Get font size by element"""
        return cls.FONT_SIZES.get(name, 10)
    
    @classmethod
    def get_dpi(cls, output_type):
        """Get DPI for output type"""
        return cls.DPI.get(output_type, 100)


class TimeSeriesLayout:
    """Layout for time series plots"""
    
    # Default layout for single panel
    SINGLE = {
        'figure_size': 'medium',
        'xlabel': 'Time (UTC)',
        'ylabel': 'Value',
        'grid': True,
        'legend': True,
        'x_rotation': 45
    }
    
    # Layout for multi-panel time series
    MULTI_PANEL = {
        'figure_size': 'wide',
        'n_cols': 2,
        'spacing': {'hspace': 0.3, 'wspace': 0.3},
        'grid': True,
        'legend': True
    }
    
    # Specific parameter layouts
    PARAM_LAYOUTS = {
        'Ey': {'ylabel': 'Ey (mV/m)', 'color': PlotStyles.PARAM_COLORS['Ey']},
        'Bz': {'ylabel': 'Bz (nT)', 'color': PlotStyles.PARAM_COLORS['Bz']},
        'P_ram': {'ylabel': 'P_ram (nPa)', 'color': PlotStyles.PARAM_COLORS['P_ram']},
        'V0': {'ylabel': 'V0 (km/s)', 'color': PlotStyles.PARAM_COLORS['V0']},
        'Kp': {'ylabel': 'Kp index', 'color': PlotStyles.PARAM_COLORS['Kp']}
    }


class MapLayout:
    """Layout for geographical maps"""
    
    # Map projections
    PROJECTIONS = {
        'global': 'cyl',
        'north_polar': 'npstere',
        'south_polar': 'spstere',
        'mercator': 'merc'
    }
    
    # Default layout
    DEFAULT = {
        'figure_size': 'large',
        'projection': 'global',
        'coastlines': True,
        'gridlines': True,
        'continents': True
    }
    
    # Station locations
    NEUTRON_MONITORS = {
        'oulu': {'lat': 65.05, 'lon': 25.47, 'name': 'Oulu'},
        'climax': {'lat': 39.37, 'lon': -106.18, 'name': 'Climax'},
        'mcmurdo': {'lat': -77.85, 'lon': 166.72, 'name': 'McMurdo'},
        'newark': {'lat': 39.68, 'lon': -75.75, 'name': 'Newark'},
        'junge': {'lat': 46.55, 'lon': 7.98, 'name': 'Jungfraujoch'}
    }
    
    # Magnetometer stations
    MAGNETOMETERS = {
        'thule': {'lat': 76.5, 'lon': -68.8, 'name': 'Thule'},
        'yellowknife': {'lat': 62.5, 'lon': -114.5, 'name': 'Yellowknife'},
        'leirvogur': {'lat': 64.2, 'lon': -21.7, 'name': 'Leirvogur'},
        'boulder': {'lat': 40.1, 'lon': -105.2, 'name': 'Boulder'},
        'kakadu': {'lat': -12.7, 'lon': 132.5, 'name': 'Kakadu'}
    }


class DashboardLayout:
    """Layout for web dashboard components"""
    
    # Dashboard sections
    SECTIONS = [
        'header',
        'solar_wind',
        'indices',
        'magnetosphere',
        'forecast',
        'alerts',
        'footer'
    ]
    
    # Grid layout (rows, columns)
    GRID = {
        'header': (0, 0, 1, 2),
        'solar_wind': (1, 0, 1, 1),
        'indices': (1, 1, 1, 1),
        'magnetosphere': (2, 0, 1, 1),
        'forecast': (2, 1, 1, 1),
        'alerts': (3, 0, 1, 2),
        'footer': (4, 0, 1, 2)
    }
    
    # Update intervals (seconds)
    UPDATE_INTERVALS = {
        'realtime': 60,
        'forecast': 3600,
        'historical': 86400
    }
    
    # Alert thresholds
    ALERT_THRESHOLDS = {
        'G4': {'color': '#ff5500', 'message': 'Severe storm - Satellite alert'},
        'G5': {'color': '#ff0000', 'message': 'Extreme storm - Grid protection'}
    }
