"""
HELIOSICA Math Utilities
Basic mathematical functions without NumPy
Pure Python implementation
"""

import math


class Stats:
    """Statistical functions"""
    
    @staticmethod
    def mean(data):
        """Calculate mean of list"""
        if not data:
            return 0.0
        return sum(data) / len(data)
    
    @staticmethod
    def median(data):
        """Calculate median of list"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        
        if n % 2 == 0:
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2
        else:
            return sorted_data[mid]
    
    @staticmethod
    def variance(data):
        """Calculate variance"""
        if len(data) < 2:
            return 0.0
        
        mu = Stats.mean(data)
        return sum((x - mu) ** 2 for x in data) / (len(data) - 1)
    
    @staticmethod
    def stddev(data):
        """Calculate standard deviation"""
        return math.sqrt(Stats.variance(data))
    
    @staticmethod
    def percentile(data, p):
        """
        Calculate percentile of data
        
        Parameters
        ----------
        data : list
            Input data
        p : float
            Percentile (0-100)
        
        Returns
        -------
        float
            Percentile value
        """
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * (p / 100.0)
        f = math.floor(k)
        c = math.ceil(k)
        
        if f == c:
            return sorted_data[int(k)]
        
        d0 = sorted_data[int(f)] * (c - k)
        d1 = sorted_data[int(c)] * (k - f)
        return d0 + d1
    
    @staticmethod
    def min_max(data):
        """Get min and max of data"""
        if not data:
            return (0.0, 0.0)
        return (min(data), max(data))
    
    @staticmethod
    def range_width(data):
        """Calculate range width"""
        if not data:
            return 0.0
        return max(data) - min(data)
    
    @staticmethod
    def quantiles(data, n=4):
        """
        Calculate n-quantiles
        
        Parameters
        ----------
        data : list
            Input data
        n : int
            Number of quantiles
        
        Returns
        -------
        list
            Quantile values
        """
        if not data:
            return []
        
        sorted_data = sorted(data)
        quantiles = []
        
        for i in range(1, n):
            p = (i / n) * 100
            quantiles.append(Stats.percentile(sorted_data, p))
        
        return quantiles


class Interpolation:
    """Interpolation functions"""
    
    @staticmethod
    def linear(x, x1, y1, x2, y2):
        """
        Linear interpolation
        
        y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
        """
        if x2 == x1:
            return y1
        
        return y1 + (x - x1) * (y2 - y1) / (x2 - x1)
    
    @staticmethod
    def log_linear(x, x1, y1, x2, y2):
        """
        Log-linear interpolation
        """
        if x2 == x1:
            return y1
        
        log_y1 = math.log(y1) if y1 > 0 else 0
        log_y2 = math.log(y2) if y2 > 0 else 0
        
        log_y = log_y1 + (x - x1) * (log_y2 - log_y1) / (x2 - x1)
        
        return math.exp(log_y)
    
    @staticmethod
    def bilinear(x, y, points):
        """
        Bilinear interpolation
        
        points: dict with (x,y) tuples as keys and values
        """
        # Find surrounding points
        x_vals = sorted(set(p[0] for p in points))
        y_vals = sorted(set(p[1] for p in points))
        
        # Find x indices
        x_low = max(v for v in x_vals if v <= x) if x <= max(x_vals) else x_vals[-2]
        x_high = min(v for v in x_vals if v >= x) if x >= min(x_vals) else x_vals[1]
        
        # Find y indices
        y_low = max(v for v in y_vals if v <= y) if y <= max(y_vals) else y_vals[-2]
        y_high = min(v for v in y_vals if v >= y) if y >= min(y_vals) else y_vals[1]
        
        # Get four corner values
        q11 = points.get((x_low, y_low), 0)
        q12 = points.get((x_low, y_high), 0)
        q21 = points.get((x_high, y_low), 0)
        q22 = points.get((x_high, y_high), 0)
        
        # Interpolate
        if x_high == x_low or y_high == y_low:
            return (q11 + q12 + q21 + q22) / 4
        
        # First in x
        r1 = Interpolation.linear(x, x_low, q11, x_high, q21)
        r2 = Interpolation.linear(x, x_low, q12, x_high, q22)
        
        # Then in y
        return Interpolation.linear(y, y_low, r1, y_high, r2)


class Polynomial:
    """Polynomial functions"""
    
    @staticmethod
    def evaluate(coeffs, x):
        """
        Evaluate polynomial at x
        
        coeffs: list [a0, a1, a2, ...] for a0 + a1*x + a2*x^2 + ...
        """
        result = 0
        for i, c in enumerate(coeffs):
            result += c * (x ** i)
        return result
    
    @staticmethod
    def derivative(coeffs):
        """
        Get derivative coefficients
        """
        return [coeffs[i] * i for i in range(1, len(coeffs))]
    
    @staticmethod
    def fit_quadratic(x1, y1, x2, y2, x3, y3):
        """
        Fit quadratic polynomial through three points
        
        Returns coefficients [a0, a1, a2]
        """
        # Solve for a0, a1, a2
        # y1 = a0 + a1*x1 + a2*x1^2
        # y2 = a0 + a1*x2 + a2*x2^2
        # y3 = a0 + a1*x3 + a2*x3^2
        
        denom = (x1 - x2) * (x1 - x3) * (x2 - x3)
        
        a0 = (x1*x2*y3*(x2 - x1) + x2*x3*y1*(x3 - x2) + x3*x1*y2*(x1 - x3)) / denom
        a1 = ( (y2 - y1)*(x1**2 - x3**2) - (y2 - y3)*(x1**2 - x2**2) ) / denom
        a2 = ( (y2 - y1)*(x1 - x3) - (y2 - y3)*(x1 - x2) ) / denom
        
        return [a0, a1, a2]


class VectorMath:
    """Vector operations"""
    
    @staticmethod
    def dot_product(v1, v2):
        """Dot product of two vectors"""
        if len(v1) != len(v2):
            raise ValueError("Vectors must have same length")
        
        return sum(v1[i] * v2[i] for i in range(len(v1)))
    
    @staticmethod
    def magnitude(v):
        """Magnitude of vector"""
        return math.sqrt(sum(x * x for x in v))
    
    @staticmethod
    def normalize(v):
        """Normalize vector to unit length"""
        mag = VectorMath.magnitude(v)
        if mag == 0:
            return v
        return [x / mag for x in v]
    
    @staticmethod
    def angle_between(v1, v2):
        """
        Angle between two vectors in radians
        """
        dot = VectorMath.dot_product(v1, v2)
        mag1 = VectorMath.magnitude(v1)
        mag2 = VectorMath.magnitude(v2)
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        cos_theta = dot / (mag1 * mag2)
        # Clamp to avoid numerical errors
        cos_theta = max(-1.0, min(1.0, cos_theta))
        
        return math.acos(cos_theta)


class RootFinding:
    """Root finding algorithms"""
    
    @staticmethod
    def bisection(f, a, b, tol=1e-6, max_iter=100):
        """
        Bisection method to find root
        
        Parameters
        ----------
        f : function
            Function to find root of
        a, b : float
            Interval [a, b] containing root
        tol : float
            Tolerance
        max_iter : int
            Maximum iterations
        
        Returns
        -------
        float
            Root approximation
        """
        fa = f(a)
        fb = f(b)
        
        if fa * fb >= 0:
            raise ValueError("Function must have opposite signs at endpoints")
        
        for _ in range(max_iter):
            c = (a + b) / 2
            fc = f(c)
            
            if abs(fc) < tol or (b - a) / 2 < tol:
                return c
            
            if fa * fc < 0:
                b = c
                fb = fc
            else:
                a = c
                fa = fc
        
        return (a + b) / 2
    
    @staticmethod
    def newton(f, df, x0, tol=1e-6, max_iter=100):
        """
        Newton's method for root finding
        
        Parameters
        ----------
        f : function
            Function to find root of
        df : function
            Derivative of f
        x0 : float
            Initial guess
        tol : float
            Tolerance
        max_iter : int
            Maximum iterations
        
        Returns
        -------
        float
            Root approximation
        """
        x = x0
        
        for _ in range(max_iter):
            fx = f(x)
            if abs(fx) < tol:
                return x
            
            dfx = df(x)
            if dfx == 0:
                raise ValueError("Zero derivative")
            
            x_new = x - fx / dfx
            
            if abs(x_new - x) < tol:
                return x_new
            
            x = x_new
        
        return x
