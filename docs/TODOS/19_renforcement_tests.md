# TODO 19 - Renforcement Couverture Tests

## Objectif

Atteindre une couverture de tests maximale en ajoutant ~80 nouveaux tests pour couvrir les gaps identifiés dans le code serveur et client.

## Contexte

Analyse de l'existant :
- **Server**: 57 tests existants, couverture ~70%
- **Mastoc**: 301 tests existants, couverture ~80%
- **Total**: 358 tests, 5723 lignes de tests

## Taches

### Phase 1: Tests Serveur (~35 tests)

- [ ] `test_users.py` - 15 tests (endpoints utilisateurs, avatar, admin)
- [ ] `test_holds.py` - 8 tests (endpoints prises)
- [ ] `test_permissions.py` - 12 tests (auth JWT/API Key, permissions)

### Phase 2: Tests Mastoc (~45 tests)

- [ ] `test_auth_manager.py` - 15 tests (login, refresh, persistence)
- [ ] `test_api_errors.py` - 12 tests (timeout, erreurs reseau)
- [ ] `test_sync.py` - 8 tests additionnels (recovery, conflicts)
- [ ] `test_integration.py` - 10 tests additionnels (full flows)

### Phase 3: Documentation

- [ ] `docs/06_guide_tests.md` - Guide pour lancer/ecrire les tests

## References

- Plan detaille: `/home/mortner/.claude/plans/spicy-wobbling-starfish.md`
- Tests serveur existants: `/server/tests/`
- Tests mastoc existants: `/mastoc/tests/`
