#!/usr/bin/env python
"""
Utility script to print fields of the first Proposicao using ProposicaoSerializer.

Note: Wrapped under __main__ so importing this module during Django test discovery
won't trigger database access before migrations are applied.
"""

if __name__ == "__main__":
    import os
    import django

    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

    from apps.pauta.models import Proposicao
    from apps.pauta.serializers import ProposicaoSerializer

    # Get first proposicao
    proposicao = Proposicao.objects.first()

    if proposicao:
        serializer = ProposicaoSerializer(proposicao)
        data = serializer.data

        print("ProposicaoSerializer now includes these fields:")
        for field in data.keys():
            print(f"  - {field}: {data[field]}")

        print(f"\nTotal fields: {len(data)}")
    else:
        print("No proposicoes found in database")
