

class LimitDecorator:

    def __init__(
            self,
            limiter: Limiter,
            limit_value: str,
            methods: Optional[Sequence[str]] = None,
    ):
