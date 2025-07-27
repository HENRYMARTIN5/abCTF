from abc import ABC, abstractmethod
import importlib
import json
import os
from typing import Dict, Optional
import markdown


class BaseChall(ABC):
    """
    This is the interface that every challenge's Python file must implement.
    """

    def __init__(self, metadata: dict, challenge_dir: str):
        self.id = metadata["id"]
        self.title = metadata["title"]
        self.category = metadata["category"]
        self.points = metadata["points"]
        self._metadata = metadata
        self._challenge_dir = challenge_dir

    @property
    def description(self) -> str:
        """Reads and renders the description markdown file."""
        desc_file = self._metadata.get("description_file", "description.md")
        try:
            with open(f"{self._challenge_dir}/{desc_file}", "r") as f:
                return markdown.markdown(f.read())
        except FileNotFoundError:
            return "Description not found for this challenge."

    @abstractmethod
    def solve(self, submitted_flag: str) -> bool:
        """
        Returns True if the submitted flag is correct, False otherwise.
        """
        pass

    @abstractmethod
    def value(self, num_solves: int) -> int:
        """
        Returns the value in points of this challenge when solved with `num_solves` existing solves from other teams.
        """
        pass


class StaticChall(BaseChall):
    """A challenge where the flag and value are static."""

    def solve(self, submitted_flag: str) -> bool:
        correct_flag = self._metadata.get("flag")
        if not correct_flag:
            return False
        return submitted_flag.strip() == correct_flag

    def value(self, num_solves: int) -> int:
        return self._metadata.get("points", 0)


class ChallengeService:
    def __init__(self, challenges_dir="challenges"):
        self.challenges_dir = challenges_dir
        self._challenges: Dict[str, BaseChall] = {}

    def load_challenges(self):
        print("--- Loading all challenges ---")
        self._challenges = {}
        for entry in os.scandir(self.challenges_dir):
            if entry.is_dir():
                challenge_dir_path = entry.path
                try:
                    with open(f"{challenge_dir_path}/chall.json", "r") as f:
                        metadata = json.load(f)

                    challenge_id = metadata["id"]

                    spec = importlib.util.spec_from_file_location(
                        name=f"challenge_module_{challenge_id}",
                        location=f"{challenge_dir_path}/chall.py",
                    )
                    challenge_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(challenge_module)

                    challenge_class = challenge_module.Challenge
                    instance = challenge_class(metadata, challenge_dir_path)

                    self._challenges[instance.id] = instance
                    print(f"  [+] Loaded challenge: {instance.title} ({instance.id})")

                except Exception as e:
                    print(
                        f"  [!] Failed to load challenge from {challenge_dir_path}: {e}"
                    )
        print("--- Challenge loading complete ---")

    def get_all_challenges(self) -> list[BaseChall]:
        return list(self._challenges.values())

    def get_challenge(self, challenge_id: str) -> Optional[BaseChall]:
        return self._challenges.get(challenge_id)
