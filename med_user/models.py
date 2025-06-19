from django.db import models

class ScreeningData(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    matrix_json = models.TextField()
    visualization = models.ImageField(upload_to='visualizations/', blank=True, null=True)
    diagnosis = models.CharField(max_length=100, blank=True, null=True)

    def get_matrix(self):
        import json
        import numpy as np
        return np.array(json.loads(self.matrix_json)).reshape(3,3)
    
    def save(self, *args, **kwargs):
        if self.pk:
            old_obj = ScreeningData.objects.get(pk=self.pk)
            if old_obj.visualization and old_obj.visualization != self.visualization:
                old_obj.visualization.delete(save=False)
        super().save(*args, **kwargs)
