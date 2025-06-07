from rest_framework import serializers
from .models import CodeExecution
import ast
import re

class CodeExecutionSerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = CodeExecution
        fields = ['id', 'code', 'output', 'status', 'session_id', 'created_at']
    
    def validate_code(self, value):
        # Check for potentially dangerous imports
        dangerous_imports = [
            'os', 'subprocess', 'sys', 'shutil', 'socket', 'requests',
            'urllib', 'ftplib', 'telnetlib', 'smtplib', 'ctypes'
        ]
        
        # Check for import statements using regex
        import_pattern = r'import\s+([\w\s,]+)|from\s+([\w\.]+)\s+import'
        imports = re.findall(import_pattern, value)
        
        # Flatten and clean the matches
        found_imports = []
        for imp_tuple in imports:
            for imp in imp_tuple:
                if imp:
                    # Split by comma and strip whitespace
                    for module in imp.split(','):
                        module = module.strip()
                        if module:
                            found_imports.append(module)
        
        # Check if any dangerous imports are found
        for dangerous_import in dangerous_imports:
            for found_import in found_imports:
                if dangerous_import == found_import or found_import.startswith(f"{dangerous_import}."):
                    raise serializers.ValidationError(f"Import of '{dangerous_import}' is not allowed for security reasons.")
        
        # Try to parse the code to check for syntax errors
        try:
            ast.parse(value)
        except SyntaxError as e:
            raise serializers.ValidationError(f"Python syntax error: {str(e)}")
            
        return value
