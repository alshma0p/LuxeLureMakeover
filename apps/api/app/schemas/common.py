from pydantic import BaseModel


disclaimer_ar = (
    "تنبيه. TeleDerma خدمة إرشادية للعناية بالبشرة والجمال فقط. غير طبية. لا تقدم تشخيصا أو علاجا. النتائج تقدير أولي وقد تخطئ. إذا كان لديك ألم أو التهاب شديد أو أعراض مقلقة فراجع مختصا مرخصا."
)


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    model_license: str
    version: str
    disclaimer_ar: str
