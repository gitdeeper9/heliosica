"""
HELIOSICA Time Utilities
Date and time handling functions
Pure Python implementation
"""

from datetime import datetime, timedelta
import re


class TimeUtils:
    """Utility functions for time operations"""
    
    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """
        Parse date string in various formats
        
        Parameters
        ----------
        date_str : str
            Date string (YYYY-MM-DD, YYYYMMDD, YYYY-MM-DD HH:MM:SS)
        
        Returns
        -------
        datetime
            Parsed datetime
        """
        # Remove any whitespace
        date_str = date_str.strip()
        
        # Try different formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y-%m-%d',
            '%Y%m%d',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%m/%d/%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    @staticmethod
    def to_doy(date: datetime) -> int:
        """
        Convert datetime to day of year
        
        Parameters
        ----------
        date : datetime
            Input date
        
        Returns
        -------
        int
            Day of year (1-366)
        """
        return date.timetuple().tm_yday
    
    @staticmethod
    def from_doy(year: int, doy: int) -> datetime:
        """
        Create datetime from year and day of year
        
        Parameters
        ----------
        year : int
            Year
        doy : int
            Day of year (1-366)
        
        Returns
        -------
        datetime
            Corresponding datetime
        """
        return datetime(year, 1, 1) + timedelta(days=doy - 1)
    
    @staticmethod
    def hours_between(start: datetime, end: datetime) -> float:
        """
        Calculate hours between two datetimes
        
        Parameters
        ----------
        start : datetime
            Start time
        end : datetime
            End time
        
        Returns
        -------
        float
            Hours between
        """
        delta = end - start
        return delta.total_seconds() / 3600.0
    
    @staticmethod
    def minutes_between(start: datetime, end: datetime) -> float:
        """
        Calculate minutes between two datetimes
        
        Parameters
        ----------
        start : datetime
            Start time
        end : datetime
            End time
        
        Returns
        -------
        float
            Minutes between
        """
        delta = end - start
        return delta.total_seconds() / 60.0
    
    @staticmethod
    def days_between(start: datetime, end: datetime) -> float:
        """
        Calculate days between two datetimes
        
        Parameters
        ----------
        start : datetime
            Start time
        end : datetime
            End time
        
        Returns
        -------
        float
            Days between
        """
        delta = end - start
        return delta.total_seconds() / 86400.0
    
    @staticmethod
    def is_leap_year(year: int) -> bool:
        """
        Check if year is leap year
        
        Parameters
        ----------
        year : int
            Year to check
        
        Returns
        -------
        bool
            True if leap year
        """
        return (year % 4 == 0) and (year % 100 != 0 or year % 400 == 0)
    
    @staticmethod
    def days_in_month(year: int, month: int) -> int:
        """
        Get number of days in month
        
        Parameters
        ----------
        year : int
            Year
        month : int
            Month (1-12)
        
        Returns
        -------
        int
            Number of days
        """
        if month == 2:
            return 29 if TimeUtils.is_leap_year(year) else 28
        if month in [4, 6, 9, 11]:
            return 30
        return 31
    
    @staticmethod
    def utc_now_str() -> str:
        """
        Get current UTC time as string
        
        Returns
        -------
        str
            Current UTC time in ISO format
        """
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format duration in seconds to human readable
        
        Parameters
        ----------
        seconds : float
            Duration in seconds
        
        Returns
        -------
        str
            Formatted duration (e.g., "2d 3h 15m")
        """
        if seconds < 60:
            return f"{seconds:.0f}s"
        
        minutes = seconds / 60
        if minutes < 60:
            return f"{minutes:.0f}m"
        
        hours = minutes / 60
        if hours < 24:
            return f"{hours:.1f}h"
        
        days = hours / 24
        return f"{days:.1f}d"
    
    @staticmethod
    def parse_duration(duration_str: str) -> float:
        """
        Parse duration string to seconds
        
        Parameters
        ----------
        duration_str : str
            Duration (e.g., "2d", "3h", "15m", "30s")
        
        Returns
        -------
        float
            Duration in seconds
        """
        duration_str = duration_str.strip().lower()
        
        # Match number and unit
        match = re.match(r'^(\d+\.?\d*)\s*([dhms])$', duration_str)
        if not match:
            raise ValueError(f"Invalid duration format: {duration_str}")
        
        value = float(match.group(1))
        unit = match.group(2)
        
        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
        else:
            raise ValueError(f"Unknown unit: {unit}")
    
    @staticmethod
    def get_carrington_rotation(date: datetime) -> float:
        """
        Calculate Carrington rotation number
        
        Parameters
        ----------
        date : datetime
            Observation date
        
        Returns
        -------
        float
            Carrington rotation number
        """
        # Carrington rotation starts on 1853-11-09
        start = datetime(1853, 11, 9)
        days = TimeUtils.days_between(start, date)
        
        # One Carrington rotation = 27.2753 days
        return 1 + days / 27.2753
    
    @staticmethod
    def get_btwn_range(start: datetime, end: datetime, 
                       interval_minutes: int) -> list:
        """
        Generate list of datetimes between start and end at given interval
        
        Parameters
        ----------
        start : datetime
            Start time
        end : datetime
            End time
        interval_minutes : int
            Interval in minutes
        
        Returns
        -------
        list
            List of datetimes
        """
        times = []
        current = start
        
        while current <= end:
            times.append(current)
            current += timedelta(minutes=interval_minutes)
        
        return times
