
from abc import ABC, abstractmethod


class Pet(ABC):
    @abstractmethod
    def express(self):
        pass

    @abstractmethod
    def getName(self):
        pass

    @abstractmethod
    def getAge(self):
        pass

    @abstractmethod
    def getAgeInHumanYears(self):
        pass


class Animal(Pet, ABC):
    def __init__(self, name, age):
        self._name = name
        self._age = age

    def happyBirthday(self):
        self._age += 1

    def getName(self):
        return self._name

    def getAge(self):
        return self._age


class Parrot(Animal):
    def express(self):
        print(f'{self.getName()}: "Hello!"')
        print(r"""
             __
            (o >
        \\\\//)
          \_/_)
           |_|
        """)

    def getAgeInHumanYears(self):
        return self.getAge() * 5


class Turtle(Animal):
    def express(self):
        print(r"""
          _____     ____
         /      \   | o |
        |        |/____/
        |________/
        |_|_| |_|_|
        """)

    def getAgeInHumanYears(self):
        age = self.getAge()

        if age <= 0:
            return 0

        return 15 + (age - 1) * 2


class Person:
    def __init__(self, name, pet=None):
        self._name = name
        self._pet = pet

    def setPet(self, pet):
        self._pet = pet

    def getPetInfo(self):
        print("--------------------")

        if self._pet is None:
            print(f"{self._name} has no pet.")
            print("--------------------")
            return

        print(f"Person: {self._name}")
        print(f"Pet name: {self._pet.getName()}")
        print(f"Age: {self._pet.getAge()} year(s)")
        print(
            f"Age in human years: "
            f"{self._pet.getAgeInHumanYears()}"
        )

        print("Pet expression:")
        self._pet.express()

        print("--------------------")


def main():
    parrot = Parrot("Parrotik", 2)
    turtle = Turtle("Turtlik", 4)

    parrot.happyBirthday()

    person1 = Person("Vika", parrot)
    person2 = Person("Masha")

    person1.getPetInfo()
    person2.getPetInfo()

    person2.setPet(turtle)
    person2.getPetInfo()


if __name__ == "__main__":
    main()
