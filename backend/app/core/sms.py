"""sms.py —— 短信发送：console 模式（开发）/ 腾讯云模式（生产）

console 模式把验证码打到日志，配合 MemoryStore 即可完整走通登陆流程；
生产切 SMS_MODE=tencent 并配置 SMS_* 环境变量（签名/模板需实名审核，提前申请）。
"""
from ..config import settings


def send_otp_sms(phone: str, code: str) -> str:
    if settings.SMS_MODE == "console":
        print(f"[sms][console] 向 {phone} 发送验证码：{code}（5 分钟内有效）")
        return "验证码已发送（开发模式：见后端日志）"

    if settings.SMS_MODE == "tencent":
        # 生产实现：tencentcloud-sdk-python 组装模板参数
        # 参数与模板 {{1}} 对齐
        from tencentcloud.common import credential  # type: ignore[import-untyped]

        try:
            # 拆分包（tencentcloud-sdk-python-sms）：模块名 sms_client
            from tencentcloud.sms.v20210111.sms_client import SmsClient
            from tencentcloud.sms.v20210111 import models as sms_models  # type: ignore
        except ImportError:
            # 整包（tencentcloud-sdk-python）：模块名 client
            from tencentcloud.sms.v20210111 import client as _sms_mod  # type: ignore
            SmsClient = _sms_mod.client  # noqa: F841
            sms_models = _sms_mod.models  # type: ignore

        cred = credential.Credential(settings.SMS_SECRET_ID, settings.SMS_SECRET_KEY)
        client = SmsClient(cred, "ap-guangzhou")
        req = sms_models.SendSmsRequest()
        req.PhoneNumberSet = [f"+86{phone}"]
        req.SmsSdkAppId = settings.SMS_SDK_APP_ID
        req.SignName = settings.SMS_SIGN_NAME
        req.TemplateId = settings.SMS_TEMPLATE_ID
        req.TemplateParamSet = [code]
        resp = client.SendSms(req)
        if resp.SendStatusSet and resp.SendStatusSet[0].Code != "Ok":
            raise RuntimeError(f"短信发送失败：{resp.SendStatusSet[0].Message}")
        return "验证码已发送，请查收短信"

    raise ValueError(f"未知 SMS_MODE：{settings.SMS_MODE}")
