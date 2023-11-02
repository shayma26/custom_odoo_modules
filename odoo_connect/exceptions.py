# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import InternalServerError, Unauthorized


class UnauthorizedMissingAuthorizationHeader(Unauthorized):
    def __init__(self):

        super().__init__(
            "You are not allowed to consume this API:\n"
        )


class UnauthorizedMalformedAuthorizationHeader(Unauthorized):
    pass


class UnauthorizedSessionMismatch(Unauthorized):
    pass


class AmbiguousJwtValidator(InternalServerError):
    pass


class JwtValidatorNotFound(InternalServerError):
    pass


class UnauthorizedInvalidToken(Unauthorized):
    pass


class UnauthorizedPartnerNotFound(Unauthorized):
    pass
