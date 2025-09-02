"""Run context for sharing state across pipeline stages."""

from dataclasses import dataclass

from cuid2 import Cuid


@dataclass
class RunContext:
    """Context object to share run state across pipeline stages."""

    run_id: str
    dry_run: bool = False
    verbose: bool = False

    @classmethod
    def create(cls, length: int = 10, dry_run: bool = False, verbose: bool = False) -> 'RunContext':
        """Create a new RunContext with generated run_id."""
        cuid_generator = Cuid(length=length)
        return cls(
            run_id=cuid_generator.generate(),
            dry_run=dry_run,
            verbose=verbose
        )
