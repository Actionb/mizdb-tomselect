from django.db import models


class SearchQueryset(models.QuerySet):
    """A queryset providing a search method."""

    def search(self, q):
        return self.filter(name__icontains=q)


class Ausgabe(models.Model):
    name = models.CharField("Ausgabe", max_length=50)
    jahr = models.CharField("Jahre", max_length=50)
    num = models.CharField("Nummer", max_length=50)
    lnum = models.CharField("lfd.Nummer", max_length=50)

    magazin = models.ForeignKey("Magazin", on_delete=models.SET_NULL, blank=True, null=True)

    objects = SearchQueryset.as_manager()

    class Meta:
        verbose_name = "Ausgabe"
        verbose_name_plural = "Ausgaben"

    def __str__(self):
        return self.name


class Magazin(models.Model):
    name = models.CharField("Magazin Name", max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Magazin"
        verbose_name_plural = "Magazine"
