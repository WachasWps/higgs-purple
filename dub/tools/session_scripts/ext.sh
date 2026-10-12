FF=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg; S=/Users/wachas/Documents/higgs-purple/dub/tools/audit_s4; V=/Users/wachas/Documents/higgs-purple/dub/Final_Deliverables/2_Product_Avatar/Purple_Sunscreen_PS/Bengali_WB
A=$V/PS_Product-Avatar_product-avatar-morning-skin-drama-again_Bengali.mp4; B=$V/PS_Product-Avatar_product-avatar-purple-tint_Bengali.mp4; C=$V/PS_Product-Avatar_product-avatar-purple-tint_Bengali_33c29291.mp4; D=$V/PS_Product-Avatar_product-avatar-purple-tint_Bengali_74495eba.mp4; E=$V/PS_Product-Avatar_product-avatar-purple-tint_Bengali_7ea55172.mp4
row(){ out=$1; f=$2; shift 2; args=(); for t in "$@"; do args+=(-ss $t -i "$f"); done; n=$#; $FF -v error -y "${args[@]}" -frames:v 1 -filter_complex "$(for i in $(seq 0 $((n-1))); do printf '[%d:v]scale=540:-1[v%d];' $i $i; done)$(for i in $(seq 0 $((n-1))); do printf '[v%d]' $i; done)hstack=inputs=$n" $S/$out.png; }
row ra $A 11.5 12.4 12.9 14.2
row rb $B 3.0 9.5 10.8 12.2
row rc $C 11.2 12.0 13.0 3.7
row rd $D 13.5 14.3 15.0 16.0
row re $E 11.2 12.5 14.7 17.5
ls $S/r*.png
