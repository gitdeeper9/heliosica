"""
HELIOSICA File I/O Utilities
File handling functions
Pure Python implementation
"""

import os
import json
import csv
from datetime import datetime


class FileUtils:
    """File handling utilities"""
    
    @staticmethod
    def ensure_dir(directory):
        """
        Ensure directory exists, create if not
        
        Parameters
        ----------
        directory : str
            Directory path
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    @staticmethod
    def read_json(filepath):
        """
        Read JSON file
        
        Parameters
        ----------
        filepath : str
            Path to JSON file
        
        Returns
        -------
        dict
            Parsed JSON data
        """
        with open(filepath, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def write_json(filepath, data, pretty=True):
        """
        Write JSON file
        
        Parameters
        ----------
        filepath : str
            Output path
        data : dict
            Data to write
        pretty : bool
            Pretty print
        """
        with open(filepath, 'w') as f:
            if pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f)
    
    @staticmethod
    def read_csv(filepath, has_header=True):
        """
        Read CSV file
        
        Parameters
        ----------
        filepath : str
            Path to CSV file
        has_header : bool
            Whether file has header row
        
        Returns
        -------
        tuple
            (header, rows) if has_header else rows
        """
        rows = []
        header = []
        
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            
            if has_header:
                header = next(reader)
            
            for row in reader:
                rows.append(row)
        
        if has_header:
            return (header, rows)
        return rows
    
    @staticmethod
    def write_csv(filepath, data, header=None):
        """
        Write CSV file
        
        Parameters
        ----------
        filepath : str
            Output path
        data : list
            List of rows
        header : list, optional
            Header row
        """
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            if header:
                writer.writerow(header)
            
            writer.writerows(data)
    
    @staticmethod
    def read_lines(filepath):
        """
        Read text file lines
        
        Parameters
        ----------
        filepath : str
            Path to text file
        
        Returns
        -------
        list
            Lines (stripped)
        """
        with open(filepath, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    
    @staticmethod
    def write_lines(filepath, lines):
        """
        Write lines to text file
        
        Parameters
        ----------
        filepath : str
            Output path
        lines : list
            Lines to write
        """
        with open(filepath, 'w') as f:
            for line in lines:
                f.write(line + '\n')
    
    @staticmethod
    def get_timestamped_filename(prefix, suffix='.json'):
        """
        Generate timestamped filename
        
        Parameters
        ----------
        prefix : str
            File prefix
        suffix : str
            File suffix
        
        Returns
        -------
        str
            Filename with timestamp
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return f"{prefix}_{timestamp}{suffix}"
    
    @staticmethod
    def safe_filename(filename):
        """
        Convert string to safe filename
        
        Parameters
        ----------
        filename : str
            Input filename
        
        Returns
        -------
        str
            Safe filename
        """
        # Replace unsafe characters
        unsafe = r'<>:"/\|?*'
        for char in unsafe:
            filename = filename.replace(char, '_')
        
        return filename
    
    @staticmethod
    def find_files(directory, pattern=None, extension=None):
        """
        Find files in directory
        
        Parameters
        ----------
        directory : str
            Directory to search
        pattern : str, optional
            Pattern to match in filename
        extension : str, optional
            File extension to filter
        
        Returns
        -------
        list
            Matching file paths
        """
        files = []
        
        for f in os.listdir(directory):
            filepath = os.path.join(directory, f)
            
            if not os.path.isfile(filepath):
                continue
            
            if extension and not f.endswith(extension):
                continue
            
            if pattern and pattern not in f:
                continue
            
            files.append(filepath)
        
        return sorted(files)
    
    @staticmethod
    def split_path(filepath):
        """
        Split filepath into components
        
        Parameters
        ----------
        filepath : str
            File path
        
        Returns
        -------
        dict
            {'dir': directory, 'name': filename, 'ext': extension}
        """
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        
        return {
            'dir': directory,
            'name': name,
            'ext': ext,
            'full': filepath
        }
    
    @staticmethod
    def human_size(size_bytes):
        """
        Convert bytes to human readable size
        
        Parameters
        ----------
        size_bytes : int
            Size in bytes
        
        Returns
        -------
        str
            Human readable size
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def get_file_info(filepath):
        """
        Get file information
        
        Parameters
        ----------
        filepath : str
            File path
        
        Returns
        -------
        dict
            File information
        """
        if not os.path.exists(filepath):
            return {'exists': False}
        
        stat = os.stat(filepath)
        
        return {
            'exists': True,
            'size': stat.st_size,
            'size_human': FileUtils.human_size(stat.st_size),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'created': datetime.fromtimestamp(stat.st_ctime),
            'is_file': os.path.isfile(filepath),
            'is_dir': os.path.isdir(filepath)
        }
    
    @staticmethod
    def backup_file(filepath, backup_dir=None):
        """
        Create backup of file
        
        Parameters
        ----------
        filepath : str
            File to backup
        backup_dir : str, optional
            Backup directory
        
        Returns
        -------
        str
            Backup file path
        """
        if not os.path.exists(filepath):
            return None
        
        if backup_dir:
            FileUtils.ensure_dir(backup_dir)
            backup_path = os.path.join(
                backup_dir,
                f"backup_{os.path.basename(filepath)}"
            )
        else:
            backup_path = filepath + '.backup'
        
        # Read original
        with open(filepath, 'rb') as src:
            data = src.read()
        
        # Write backup
        with open(backup_path, 'wb') as dst:
            dst.write(data)
        
        return backup_path
    
    @staticmethod
    def merge_dicts(dict1, dict2):
        """
        Merge two dictionaries recursively
        
        Parameters
        ----------
        dict1 : dict
            Base dictionary
        dict2 : dict
            Dictionary to merge in
        
        Returns
        -------
        dict
            Merged dictionary
        """
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = FileUtils.merge_dicts(result[key], value)
            else:
                result[key] = value
        
        return result
