{
    # First print the tree structure
    tree -I 'log|install|build|.git'
    
    echo -e "\n=== FILE CONTENTS ===\n"
    
    # Then print contents of each file
    find . -type f \
        -not -path '*/log/*' \
        -not -path '*/install/*' \
        -not -path '*/build/*' \
        -not -path '*/.git/*' \
        -print0 | while IFS= read -r -d '' file; do
        echo -e "\n=== $file ===\n"
        cat "$file" 2>/dev/null || echo "[Binary file or unable to read]"
        echo -e "\n-------------------\n"
    done
} > OUTPUT