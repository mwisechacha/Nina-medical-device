from django.db import models

class ScreeningData(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    matrix_json = models.TextField()
    diagnosis = models.CharField(max_length=100, blank=True, null=True)

    def get_matrix(self):
        import json
        import numpy as np
        return np.array(json.loads(self.matrix_json)).reshape(3,3)