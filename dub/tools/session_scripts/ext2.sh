FF=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg; S=/Users/wachas/Documents/higgs-purple/dub/tools/audit_s4; V=/Users/wachas/Documents/higgs-purple/dub/Final_Deliverables/2_Product_Avatar/Purple_Sunscreen_PS/Bengali_WB
C=$V/PS_Product-Avatar_product-avatar-purple-tint_Bengali_33c29291.mp4; B=$V/PS_Product-Avatar_product-avatar-purple-tint_Bengali.mp4
row(){ out=$1; f=$2; shift 2; args=(); for t in "$@"; do args+=(-ss $t -i "$f"); done; n=$#; $FF -v error -y "${args[@]}" -frames:v 1 -filter_complex "$(for i in $(seq 0 $((n-1))); do printf '[%d:v]scale=540:-1[v%d];' $i $i; done)$(for i in $(seq 0 $((n-1))); do printf '[v%d]' $i; done)hstack=inputs=$n" $S/$out.png; }
row rc2 $C 12.7 12.95 13.2 13.45
row rb2 $B 14.2 17.5 1.0 0.3
