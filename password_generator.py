import random
import string
import re

class PasswordGenerator:
    """Generates secure random passwords with customizable options."""
    
    def __init__(self):
        """Initialize the password generator."""
        # Default settings
        self.length = 16
        self.include_uppercase = True
        self.include_lowercase = True
        self.include_numbers = True
        self.include_symbols = True
        self.exclude_similar = False
        self.exclude_ambiguous = False
        
        # Character sets
        self.uppercase_chars = string.ascii_uppercase
        self.lowercase_chars = string.ascii_lowercase
        self.number_chars = string.digits
        self.symbol_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?/"
        self.similar_chars = "il1Lo0O"
        self.ambiguous_chars = "{}[]()/\\'\"`~,;:.<>"
        
    def generate_password(self, 
                         length=None, 
                         include_uppercase=None,
                         include_lowercase=None,
                         include_numbers=None,
                         include_symbols=None,
                         exclude_similar=None,
                         exclude_ambiguous=None):
        """
        Generate a password with the specified options.
        
        Args:
            length: Length of the password
            include_uppercase: Whether to include uppercase letters
            include_lowercase: Whether to include lowercase letters
            include_numbers: Whether to include numbers
            include_symbols: Whether to include symbols
            exclude_similar: Whether to exclude similar characters
            exclude_ambiguous: Whether to exclude ambiguous characters
            
        Returns:
            str: Generated password
        """
        # Update options if provided
        if length is not None:
            self.length = length
        if include_uppercase is not None:
            self.include_uppercase = include_uppercase
        if include_lowercase is not None:
            self.include_lowercase = include_lowercase
        if include_numbers is not None:
            self.include_numbers = include_numbers
        if include_symbols is not None:
            self.include_symbols = include_symbols
        if exclude_similar is not None:
            self.exclude_similar = exclude_similar
        if exclude_ambiguous is not None:
            self.exclude_ambiguous = exclude_ambiguous
            
        # Build character set
        char_set = ""
        required_chars = []
        
        if self.include_uppercase:
            chars = self.uppercase_chars
            if self.exclude_similar:
                chars = ''.join(c for c in chars if c not in self.similar_chars)
            if self.exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.ambiguous_chars)
            char_set += chars
            if chars:
                required_chars.append(random.choice(chars))
                
        if self.include_lowercase:
            chars = self.lowercase_chars
            if self.exclude_similar:
                chars = ''.join(c for c in chars if c not in self.similar_chars)
            if self.exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.ambiguous_chars)
            char_set += chars
            if chars:
                required_chars.append(random.choice(chars))
                
        if self.include_numbers:
            chars = self.number_chars
            if self.exclude_similar:
                chars = ''.join(c for c in chars if c not in self.similar_chars)
            char_set += chars
            if chars:
                required_chars.append(random.choice(chars))
                
        if self.include_symbols:
            chars = self.symbol_chars
            if self.exclude_ambiguous:
                chars = ''.join(c for c in chars if c not in self.ambiguous_chars)
            char_set += chars
            if chars:
                required_chars.append(random.choice(chars))
                
        # Ensure we have characters to choose from
        if not char_set:
            raise ValueError("No characters available with current settings")
            
        # Generate password
        if len(required_chars) > self.length:
            required_chars = required_chars[:self.length]
            
        password_chars = required_chars
        
        # Fill remaining length with random characters
        remaining_length = self.length - len(password_chars)
        password_chars.extend(random.choice(char_set) for _ in range(remaining_length))
        
        # Shuffle the password characters
        random.shuffle(password_chars)
        
        return ''.join(password_chars)
    
    def calculate_strength(self, password):
        """
        Calculate the strength of a password.
        
        Args:
            password: The password to check
            
        Returns:
            tuple: (score, feedback) where score is 0-100 and feedback is a string
        """
        if not password:
            return 0, "Password is empty"
            
        score = 0
        feedback = []
        
        # Length check
        length = len(password)
        if length < 8:
            score += length * 2  # 2 points per character for short passwords
            feedback.append("Password is too short")
        elif length < 12:
            score += 16 + (length - 8) * 3  # 16 for minimum + 3 points per additional character
        else:
            score += 28 + min(length - 12, 12) * 2  # 28 for 12 chars + 2 points per additional (max 24 more points)
            
        # Character variety
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_symbol = bool(re.search(r'[^a-zA-Z0-9]', password))
        
        variety_score = 0
        if has_lower:
            variety_score += 5
        else:
            feedback.append("Add lowercase letters")
            
        if has_upper:
            variety_score += 5
        else:
            feedback.append("Add uppercase letters")
            
        if has_digit:
            variety_score += 5
        else:
            feedback.append("Add numbers")
            
        if has_symbol:
            variety_score += 10
        else:
            feedback.append("Add symbols")
            
        # Bonus for combination of character types
        char_type_count = sum([has_lower, has_upper, has_digit, has_symbol])
        if char_type_count >= 3:
            variety_score += 5
        if char_type_count >= 4:
            variety_score += 5
            
        score += variety_score
        
        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):  # Repeated characters
            score -= 10
            feedback.append("Avoid repeated characters")
            
        if re.search(r'(123|234|345|456|567|678|789|987|876|765|654|543|432|321)', password):
            score -= 10
            feedback.append("Avoid sequential numbers")
            
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz|zyx|yxw|xwv|wvu|vut|uts|tsr|srq|rqp|qpo|pon|onm|nml|mlk|lkj|kji|jih|ihg|hgf|gfe|fed|edc|dcb|cba)', password.lower()):
            score -= 10
            feedback.append("Avoid sequential letters")
            
        # Clamp score between 0-100
        score = max(0, min(100, score))
        
        # Generate feedback message
        if score >= 80:
            strength_feedback = "Very strong password"
        elif score >= 60:
            strength_feedback = "Strong password"
        elif score >= 40:
            strength_feedback = "Moderate password"
        elif score >= 20:
            strength_feedback = "Weak password"
        else:
            strength_feedback = "Very weak password"
            
        if feedback:
            strength_feedback += ": " + ", ".join(feedback)
            
        return score, strength_feedback
