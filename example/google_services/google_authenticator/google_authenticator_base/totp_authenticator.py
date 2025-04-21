import pyotp
import qrcode
from PIL import Image


# 1. 生成一個新的 TOTP 秘鑰
def generate_totp_key():
    totp = pyotp.TOTP(pyotp.random_base32())
    return totp


# 2. 生成 QR 碼
def generate_qr_code(totp, user_email, issuer_name):
    # 設定帳號資訊和 issuer 名稱
    uri = totp.provisioning_uri(name=user_email, issuer_name=issuer_name)

    # 生成 QR 碼
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img.save('qrcode.png')

    # 自動打開圖片
    img = Image.open('qrcode.png')
    img.show()

    print(f'QR code saved as qrcode.png. Scan this with Google Authenticator.')


# 3. 驗證 OTP
def verify_otp(totp, otp_code):
    return totp.verify(otp_code)


if __name__ == "__main__":
    # 設定使用者電子郵件和發行者名稱
    user_email = 'user@example.com'
    issuer_name = 'MyApp'

    # 生成 TOTP 密鑰
    totp = generate_totp_key()

    # 生成 QR 碼
    generate_qr_code(totp, user_email, issuer_name)

    # 輸入從 Google Authenticator 應用程式中獲取的 OTP
    otp_code = input('Enter the OTP code from Google Authenticator: ')

    # 驗證 OTP
    if verify_otp(totp, otp_code):
        print('OTP is valid!')
    else:
        print('Invalid OTP!')
