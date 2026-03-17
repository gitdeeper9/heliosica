"""
HELIOSICA Visualization Formatters
Format data for display and plotting
Pure Python
"""

from datetime import datetime
import math


class DataFormatters:
    """Format data for display"""
    
    @staticmethod
    def format_timestamp(dt, format='iso'):
        """Format timestamp for display"""
        if not isinstance(dt, datetime):
            return str(dt)
        
        if format == 'iso':
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        elif format == 'date':
            return dt.strftime('%Y-%m-%d')
        elif format == 'time':
            return dt.strftime('%H:%M:%S')
        elif format == 'compact':
            return dt.strftime('%Y%m%d_%H%M%S')
        else:
            return str(dt)
    
    @staticmethod
    def format_value(value, unit='', precision=2):
        """Format value with unit"""
        if value is None:
            return 'N/A'
        
        if isinstance(value, float):
            fmt = f"{{:.{precision}f}}"
            return f"{fmt.format(value)} {unit}".strip()
        
        return f"{value} {unit}".strip()
    
    @staticmethod
    def format_scientific(value, precision=2):
        """Format in scientific notation"""
        if value is None or value == 0:
            return '0'
        
        exponent = int(math.floor(math.log10(abs(value))))
        mantissa = value / (10 ** exponent)
        
        return f"{mantissa:.{precision}f} × 10^{exponent}"
    
    @staticmethod
    def format_percent(value, precision=1):
        """Format as percentage"""
        return f"{value * 100:.{precision}f}%"
    
    @staticmethod
    def format_kp(kp_value):
        """Format Kp index"""
        if kp_value is None:
            return 'N/A'
        
        if kp_value >= 9:
            return '9+'
        elif kp_value >= 8:
            return '8-9'
        elif kp_value >= 7:
            return '7-8'
        elif kp_value >= 6:
            return '6-7'
        elif kp_value >= 5:
            return '5-6'
        elif kp_value >= 4:
            return '4-5'
        elif kp_value >= 3:
            return '3-4'
        elif kp_value >= 2:
            return '2-3'
        elif kp_value >= 1:
            return '1-2'
        else:
            return '0-1'
    
    @staticmethod
    def format_g_category(kp_value):
        """Convert Kp to G-scale category"""
        if kp_value >= 9:
            return 'G5'
        elif kp_value >= 8:
            return 'G4'
        elif kp_value >= 7:
            return 'G3'
        elif kp_value >= 6:
            return 'G2'
        elif kp_value >= 5:
            return 'G1'
        else:
            return 'G0'
    
    @staticmethod
    def format_storm_name(kp_value):
        """Get storm name from Kp"""
        if kp_value >= 9:
            return 'Extreme'
        elif kp_value >= 8:
            return 'Severe'
        elif kp_value >= 7:
            return 'Strong'
        elif kp_value >= 6:
            return 'Moderate'
        elif kp_value >= 5:
            return 'Minor'
        else:
            return 'Quiet'
    
    @staticmethod
    def format_coordinates(lat, lon, format='dms'):
        """Format coordinates"""
        if format == 'dms':
            lat_dir = 'N' if lat >= 0 else 'S'
            lon_dir = 'E' if lon >= 0 else 'W'
            
            lat_abs = abs(lat)
            lon_abs = abs(lon)
            
            lat_deg = int(lat_abs)
            lat_min = int((lat_abs - lat_deg) * 60)
            lat_sec = ((lat_abs - lat_deg) * 60 - lat_min) * 60
            
            lon_deg = int(lon_abs)
            lon_min = int((lon_abs - lon_deg) * 60)
            lon_sec = ((lon_abs - lon_deg) * 60 - lon_min) * 60
            
            return (f"{lat_deg}°{lat_min}'{lat_sec:.0f}\"{lat_dir} "
                    f"{lon_deg}°{lon_min}'{lon_sec:.0f}\"{lon_dir}")
        
        else:  # decimal
            return f"{lat:.2f}°, {lon:.2f}°"
    
    @staticmethod
    def format_duration(seconds):
        """Format duration in seconds"""
        if seconds < 60:
            return f"{seconds:.0f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
        else:
            days = seconds / 86400
            return f"{days:.1f} days"
    
    @staticmethod
    def format_file_size(bytes):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} TB"
    
    @staticmethod
    def format_list(items, max_items=5):
        """Format list for display"""
        if len(items) <= max_items:
            return ', '.join(str(i) for i in items)
        else:
            first = ', '.join(str(i) for i in items[:max_items])
            return f"{first} ... and {len(items) - max_items} more"
    
    @staticmethod
    def format_dict(data, indent=0):
        """Format dictionary for display"""
        lines = []
        spaces = '  ' * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{spaces}{key}:")
                lines.append(DataFormatters.format_dict(value, indent + 1))
            else:
                lines.append(f"{spaces}{key}: {value}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def format_alert_message(category, value):
        """Format alert message"""
        messages = {
            'G4': f"⚠️ SEVERE STORM (G4): GSSI = {value:.3f} - Satellite operators advised to enter safe mode",
            'G5': f"🚨 EXTREME STORM (G5): GSSI = {value:.3f} - Emergency protocols activated"
        }
        return messages.get(category, f"Storm alert: {category} ({value:.3f})")


class AxisFormatters:
    """Format axis labels and ticks"""
    
    @staticmethod
    def time_axis(timestamps):
        """Format time axis ticks"""
        if not timestamps:
            return []
        
        # Determine appropriate format based on range
        first = timestamps[0]
        last = timestamps[-1]
        span = (last - first).total_seconds()
        
        if span < 3600:  # < 1 hour
            format = '%H:%M:%S'
        elif span < 86400:  # < 1 day
            format = '%H:%M'
        elif span < 604800:  # < 1 week
            format = '%m-%d %H:%M'
        else:
            format = '%Y-%m-%d'
        
        return [t.strftime(format) for t in timestamps]
    
    @staticmethod
    def scientific_ticks(min_val, max_val):
        """Generate scientific notation ticks"""
        if min_val == max_val:
            return [min_val]
        
        # Calculate nice tick positions
        range_val = max_val - min_val
        exponent = math.floor(math.log10(range_val))
        step = 10 ** exponent
        
        start = math.floor(min_val / step) * step
        ticks = []
        
        val = start
        while val <= max_val:
            if val >= min_val:
                ticks.append(val)
            val += step
        
        return ticks
    
    @staticmethod
    def log_ticks(min_val, max_val):
        """Generate logarithmic ticks"""
        if min_val <= 0:
            min_val = 1e-10
        
        min_exp = math.floor(math.log10(min_val))
        max_exp = math.ceil(math.log10(max_val))
        
        ticks = []
        for exp in range(min_exp, max_exp + 1):
            val = 10 ** exp
            if min_val <= val <= max_val:
                ticks.append(val)
        
        return ticks


class ColorBarFormatter:
    """Format color bars"""
    
    @staticmethod
    def get_temperature_ticks(temp_min, temp_max):
        """Get ticks for temperature colorbar"""
        # Temperature typically in K, use 1000K steps
        step = 1000
        start = math.floor(temp_min / step) * step
        ticks = []
        
        val = start
        while val <= temp_max:
            if val >= temp_min:
                ticks.append(val)
            val += step
        
        return ticks
    
    @staticmethod
    def get_pressure_ticks(p_min, p_max):
        """Get ticks for pressure colorbar"""
        # Pressure in nPa, log scale often better
        return AxisFormatters.log_ticks(p_min, p_max)
    
    @staticmethod
    def get_velocity_ticks(v_min, v_max):
        """Get ticks for velocity colorbar"""
        # Velocity in km/s, use 100 km/s steps
        step = 100
        start = math.floor(v_min / step) * step
        ticks = []
        
        val = start
        while val <= v_max:
            if val >= v_min:
                ticks.append(val)
            val += step
        
        return ticks
    
    @staticmethod
    def get_gssi_ticks():
        """Get ticks for GSSI colorbar"""
        return [0.0, 0.2, 0.45, 0.7, 1.0]
    
    @staticmethod
    def get_gssi_labels():
        """Get labels for GSSI colorbar"""
        return ['G0-G1', 'G2-G3', 'G4', 'G5']
