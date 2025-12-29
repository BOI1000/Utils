#!/usr/bin/env bash

# PBKDF2 to Hashcat format converter
# author: Me
# Usage: pbkdf2-hashcat.sh <hash | hashfile> [options]
# hashcat format: sha256:600000:OCpzO4Ehe4pwIulnzs6uRA==:a471b5becdda28104263875dda3b211c
# hashcat mode: 10900 (PBKDF2-HMAC-SHA256)
# credits and references:
#   - Original idea and implementation:
#   - https://notes.benheater.com/books/hash-cracking/page/pbkdf2-hmac-sha256


usage() {
    cat <<'USAGE' >&2
Usage: pbkdf2-hashcat.sh <hash_or_file> [options]

Options:
  -h, --help        Show this help and exit
      --encode-salt Enable encoding of salt
USAGE
}

process_hash() {
    if ! [[ "$hash" =~ ^pbkdf2 ]]; then
        echo "[-] Unsupported hash format: $hash" >&2
        echo "[-] Expected format: pbkdf2:number_of_iterations:<base64_salt>:<hex_hash>" >&2
        exit 1
    fi

    number_of_iterations=$(awk -F'[:$]' '{print $3; exit}' <<< "$hash")
    hex_encoded_hash=$(printf "$hash" | cut -d'$' -f3)
    b64_encoded_salt=$(printf "$hash" | cut -d'$' -f2)
    algorithm=$(printf "$hash" | cut -d':' -f2)

    base64_encoded_hash=$(echo -n "$hex_encoded_hash" | xxd -r -p | base64)

    encode_salt_option=$encode_salt

    if [ "$encode_salt_option" = true ]; then
        b64_encoded_salt=$(echo -n "$b64_encoded_salt" | base64)
        new_hash="${algorithm}:${number_of_iterations}:${b64_encoded_salt}:${base64_encoded_hash}"
    else
        new_hash="${algorithm}:${number_of_iterations}:${b64_encoded_salt}:${base64_encoded_hash}"
    fi
}

show_help=false
encode_salt=false
positional=()

while [ "$#" -gt 0 ]; do
    case "$1" in
        -h|--help) show_help=true; shift ;;
        --encode-salt) encode_salt=true; shift ;;
        --) shift; break ;;
        -*) echo "Unknown option: $1" >&2; usage; exit 1 ;;
        *) positional+=("$1"); shift ;;
    esac
done

if [ "$show_help" = true ]; then
    usage
    exit 0
fi

if [ "${#positional[@]}" -lt 1 ]; then
    echo "Error: missing <hash_or_file>" >&2
    usage
    exit 1
fi

if [ -f "${positional[0]}" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
        hash="${line%%$'\r'}"
        [[ -z ${hash//[[:space:]]/} ]] && continue
        [[ $line = \#* ]] && continue
        process_hash
        echo "$new_hash"
    done < "${positional[0]}"
else
    hash="${positional[0]}"
    process_hash
    echo "$new_hash"
fi