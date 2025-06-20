from django.db import models


class Person(models.Model):
    full_name = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    dob = models.DateField(blank=True, null=True)
    city = models.ForeignKey("City", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        elif " " in self.full_name:
            self.first_name, self.last_name = self.full_name.rsplit(" ", 1)
        else:
            self.last_name = self.full_name
        super().save(*args, **kwargs)

    name_field = "full_name"
    create_field = "full_name"

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "Persons"
        ordering = ["last_name", "first_name"]


class City(models.Model):
    name = models.CharField(max_length=50)

    name_field = "name"
    create_field = "name"

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Genre(models.Model):
    genre = models.CharField(max_length=50, unique=True)

    name_field = "genre"
    create_field = "genre"

    class Meta:
        verbose_name = "Genre"
        verbose_name_plural = "Genres"
        ordering = ["genre"]
