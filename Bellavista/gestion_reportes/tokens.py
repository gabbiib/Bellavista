from django.contrib.auth.tokens import PasswordResetTokenGenerator

def int_to_bytes(i):
    return i.to_bytes((i.bit_length() + 7) // 8, byteorder='big')

account_activation_token = PasswordResetTokenGenerator()