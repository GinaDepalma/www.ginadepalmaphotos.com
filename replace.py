import os

def replace_in_file(file_path, old_string, new_string):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        content = content.replace(old_string, new_string)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

def main():
    files_to_process = [
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\1-x-bet-tr-platformunda-spor-bahisleri-ve-casino-oyunlarinda-kazanc-sansi\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\16701\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\1xbet-apk-i╠çndir-turkiyede-guvenli-bahis\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\1xbet-platformuna-kolay-ve-hizli-erisim\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\2025te-guvenilir-deneme-bonusu-nereden-alinir\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\7bit-leading-online-casino-for-australian-players\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\about-us-6\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\addimlar-mostbet-ile-tehlukesiz-bahis-tecrubesi-ucun\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\author\admin\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\author\admin\page\2\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\author\admin\page\3\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\author\admin\page\4\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\author\admin\page\5\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\author\designsarena\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\azino-777-kazino\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\azino-777-mobayl\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\bahis-dunyasinda-1x-bet-ile-guvenli-ve-kazancli-adimlar\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\bahsegel-sorunsuz-giris-icin-dikkat-etmeniz-gerekenler-nelerdir\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\blog-4\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\blog-4\page\2\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\blog-4\page\3\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\blog-4\page\4\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\blog-4\page\5\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\buyuk-kazanc-firsatlari-sunan-pinup-casinoyu-kesfedin\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\casibom-casino\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\casino-maceraniza-1king-ile-baslayin\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\casino-mate-exploring-the-best-games-and-promotions\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\casinonic-casino-australia-delivers-secure-access\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\category\reviews\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\category\uncategorized\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\category\uncategorized\page\2\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\category\uncategorized\page\3\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\category\uncategorized\page\4\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\contact-4\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\discover-the-diverse-game-selection-for-australian-players-at-fairgocasino\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\discovering-the-game-selection-for-australian-players-at-ozwincasino\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\explore-the-variety-of-games-at-oz-win-for-australian-players\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\extras-en-kansspelen-online-casino-betsixty\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\fair-go-accessing-casino-site-on-ios\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\glory-casino-online-a-trusted-casino-for-bangladeshi-players\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\glory-casino-turkiye-resmi-adres\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\glory-casino-turkiye-resmi-site-ve-sunulan-avantajlar\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\got-me-hard-very-fast-i-almost-came-in-my-pants\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\guvenli-bahis-deneyimi-icin-adimlar-1x-bet-platformunda\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\heyecan-ve-kazanc-gatesofolympus-slot-oyunu\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\home-16\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\i-felt-much-better-by-the-time-i-left\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\igrovie-avtomati-riobet-obhod-blokirovki-oficialynogo-sayta\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\kazanmaya-baslamak-icin-glory-casino-casino-glory-glorycasino-casinoglory-giris-ve-bonuslar\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\most-bet-casino-oyunlari-ve-bahisler\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\mostbet-az-hemise-yenilenen-oyunlar\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\mostbet-ile-genis-bahis-secenekleri\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\mostbet-platformasina-daxil-olmaq-ve-bonuslardan-istifade-et\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\mostbet-uz-online-kazino-oyinlarida-omadingizni-sinang\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\my-honeys-birthday-celebration-with-porn-star-was-definitely-more-than-we-expected\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\my-video-store\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\my-yahoo-stores\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\osobennosti-topovoy-igrovoy-ploshtadki-azino-777-vhod-oficialynoe-zerkalo\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\ozwin-casino-au-caters-to-mobilefirst-aussie-bettors\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\portfolio-3\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\portfolio_page\gina-de-palma\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\portfolio_page\girl-on-girl\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\portfolio_page\hot-couples\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\portfolio_page\orgies\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\portfolio_page\videos\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\rates-gina-depalma\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\raznoobrazie-igrovih-avtomatov-admiral-h-bezdepozitniy-bonus-poraduet-azartnih-igrokov\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\reviews\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\ripper-casino-au-welcomes-players-with-exclusive-vip-benefits\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\sekabet-giris-hizli-ve-guvenli-casino-platformu\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\she-rocked-my-world-when-she-popped-my-cherry\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\shes-amazing-better-than-any-movie-youve-see-out-there\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\streaming-movies\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\successful-mostbet-casino-login-2024\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\ummmm-how-about-the-best-sex-ive-ever-had\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\unlocking-the-full-potential-of-rewards-at-australias-fairgo-casino\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\you-are-beautiful-and-wonderful\index.html",
        "C:\Users\Owner\OneDrive\Documents\GitHub\www.ginadepalmaphotos.com\yuksek-kazanc-potansiyeli-ve-eglence-sunan-bonanza-slotu\index.html",
    ]

    for file_path in files_to_process:
        # Remove reservation menu item
        old_string = '<li id="nav-menu-item-21977" class="menu-item menu-item-type-custom menu-item-object-custom  narrow"><a href="../reservation-form/" class=""><i class="menu_icon blank fa"></i><span>Reservation</span><span class="plus"></span></a></li>'
        new_string = ''
        replace_in_file(file_path, old_string, new_string)

        # Remove reservation mobile menu item
        old_string = """<li id="mobile-menu-item-21977" class="menu-item menu-item-type-custom menu-item-object-custom ">
<a href="../reservation-form/" class=""><span>Reservation</span></a><span class="mobile_arrow"><i class="fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>
</li>"""
        new_string = ''
        replace_in_file(file_path, old_string, new_string)

        # Rename contact to reservation
        old_string = '<li id="nav-menu-item-16676" class="menu-item menu-item-type-post_type menu-item-object-page  narrow"><a href="../contact-4/" class=""><i class="menu_icon blank fa"></i><span>Contact</span><span class="plus"></span></a></li>'
        new_string = '<li id="nav-menu-item-16676" class="menu-item menu-item-type-post_type menu-item-object-page  narrow"><a href="../contact-4/" class=""><i class="menu_icon blank fa"></i><span>Reservation</span><span class="plus"></span></a></li>'
        replace_in_file(file_path, old_string, new_string)

        # Rename contact to reservation in mobile
        old_string = """<li id="mobile-menu-item-16676" class="menu-item menu-item-type-post_type menu-item-object-page ">
<a href="../contact-4/" class=""><span>Contact</span></a><span class="mobile_arrow"><i class="fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>
</li>"""
        new_string = """<li id="mobile-menu-item-16676" class="menu-item menu-item-type-post_type menu-item-object-page ">
<a href="../contact-4/" class=""><span>Reservation</span></a><span class="mobile_arrow"><i class="fa fa-angle-right"></i><i class="fa fa-angle-down"></i></span>
</li>"""
        replace_in_file(file_path, old_string, new_string)
        
        # Remove reservation form link from rates page
        old_string = '<p>I only see ONE New client a day with 48-72 hrs. Notice. A proper introduction, text to confirm 917 256 1116 Please use my reservation-form</p>'
        new_string = ''
        replace_in_file(file_path, old_string, new_string)

        old_string = '<p><a href="../reservation-form/">/reservation-form/</a>				No form, no discount offered</p>'
        new_string = ''
        replace_in_file(file_path, old_string, new_string)

if __name__ == '__main__':
    main()
