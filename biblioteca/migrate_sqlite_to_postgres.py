"""
Script de migração: SQLite → PostgreSQL
========================================
Executa UMA ÚNICA VEZ para copiar todos os dados do banco SQLite local
para o PostgreSQL provisionado pelo Railway.

Pré-requisitos:
  1. DATABASE_URL apontando para o PostgreSQL já configurada no ambiente.
  2. Schema criado: python manage.py migrate

Como executar (dentro do diretório biblioteca/):
  python migrate_sqlite_to_postgres.py
"""

import os
import sys
import django
import sqlite3

# Garante que o settings do projeto seja encontrado independente de onde
# o script é chamado.
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from django.contrib.auth.models import User  # noqa: E402
from core.models import Livro, Emprestimo    # noqa: E402


def migrate_sqlite_to_postgres():
    """Copia dados do SQLite para o PostgreSQL configurado em DATABASE_URL."""

    sqlite_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    if not os.path.exists(sqlite_path):
        print(f"❌ Arquivo SQLite não encontrado: {sqlite_path}")
        return

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()

    try:
        # ------------------------------------------------------------------ #
        # 1. Usuários                                                         #
        # ------------------------------------------------------------------ #
        print("Migrando usuários...")
        cursor.execute(
            "SELECT id, username, email, password, is_staff, is_superuser, "
            "is_active, first_name, last_name, date_joined, last_login "
            "FROM auth_user"
        )
        users_map: dict[int, int] = {}  # sqlite_id → postgres_id

        for row in cursor.fetchall():
            user, created = User.objects.get_or_create(
                username=row['username'],
                defaults={
                    'email': row['email'],
                    'password': row['password'],
                    'is_staff': bool(row['is_staff']),
                    'is_superuser': bool(row['is_superuser']),
                    'is_active': bool(row['is_active']),
                    'first_name': row['first_name'] or '',
                    'last_name': row['last_name'] or '',
                },
            )
            users_map[row['id']] = user.id
            status = '✓ criado' if created else '· já existe'
            print(f"  {status}: {row['username']}")

        # ------------------------------------------------------------------ #
        # 2. Livros                                                           #
        # ------------------------------------------------------------------ #
        print("\nMigrando livros...")
        cursor.execute(
            "SELECT id, titulo, autor, isbn, quantidade FROM core_livro"
        )
        livros_map: dict[int, int] = {}  # sqlite_id → postgres_id

        for row in cursor.fetchall():
            livro, created = Livro.objects.get_or_create(
                isbn=row['isbn'],
                defaults={
                    'titulo': row['titulo'],
                    'autor': row['autor'],
                    'quantidade': row['quantidade'],
                },
            )
            livros_map[row['id']] = livro.id
            status = '✓ criado' if created else '· já existe'
            print(f"  {status}: {row['titulo']}")

        # ------------------------------------------------------------------ #
        # 3. Empréstimos                                                      #
        # ------------------------------------------------------------------ #
        print("\nMigrando empréstimos...")
        cursor.execute(
            "SELECT id, usuario_id, livro_id, data_emprestimo, "
            "data_devolucao, devolvido FROM core_emprestimo"
        )

        migrated = skipped = 0
        for row in cursor.fetchall():
            usuario_id = users_map.get(row['usuario_id'])
            livro_id = livros_map.get(row['livro_id'])

            if not usuario_id or not livro_id:
                print(
                    f"  ⚠ Empréstimo id={row['id']} ignorado "
                    f"(usuario_id={row['usuario_id']} ou "
                    f"livro_id={row['livro_id']} não encontrado)"
                )
                skipped += 1
                continue

            _, created = Emprestimo.objects.get_or_create(
                usuario_id=usuario_id,
                livro_id=livro_id,
                data_emprestimo=row['data_emprestimo'],
                defaults={
                    'data_devolucao': row['data_devolucao'],
                    'devolvido': bool(row['devolvido']),
                },
            )
            if created:
                migrated += 1

        print(f"  ✓ {migrated} empréstimo(s) criado(s), {skipped} ignorado(s)")

        print("\n✅ Migração concluída com sucesso!")

    except Exception as exc:
        print(f"\n❌ Erro durante a migração: {exc}")
        raise
    finally:
        sqlite_conn.close()


if __name__ == '__main__':
    migrate_sqlite_to_postgres()
