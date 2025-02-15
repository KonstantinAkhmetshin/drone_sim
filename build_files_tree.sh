{
    # First print the tree structure
    tree -I 'log|install|build|.git|AirSimNH|venv|__pycache__|*.png'
    
    echo -e "\n=== FILE CONTENTS ===\n"
    
    # Then print contents of each file
    find . -type f \
        -not -path '*/log/*' \
        -not -path '*/install/*' \
        -not -path '*/build/*' \
        -not -path '*/.git/*' \
        -not -name '*.png' \
        -not -path '*/AirSimNH/*' \
        -not -path '*/venv/*' \
        -not -path '*/__pycache__/*' \
        -print0 | while IFS= read -r -d '' file; do
        echo -e "\n=== $file ===\n"
        cat "$file" 2>/dev/null || echo "[Binary file or unable to read]"
        echo -e "\n-------------------\n"
    done
} > porject_structure.info