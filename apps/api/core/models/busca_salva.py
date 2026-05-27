from django.contrib.auth.models import User
from django.db import models


class BuscaSalva(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buscas_salvas')
    title = models.CharField(max_length=150)
    query = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Busca Salva'
        verbose_name_plural = 'Buscas Salvas'

    def __str__(self) -> str:
        return f"{self.title} ({self.user.email})"
