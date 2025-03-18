from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the year, summary, and employee id values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        if self.id is None:
            sql = "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)"
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        else:
            self.update()
        pass

    @classmethod
    def create(cls, year, summary, employee_id):
        """ Initialize a new Review instance and save the object to the database. Return the new instance. """
        review = cls(year, summary, employee_id)
        review.save()
        return review
        pass
   
    @classmethod
    def instance_from_db(cls, row):
        """Return an Review instance having the attribute values from the table row."""
        # Check the dictionary for  existing instance using the row's primary key
        if row is None:
            return None
        review_id = row[0]
        if review_id in cls.all:
            # update instance in case the db row has changed
            instance = cls.all[review_id]
            instance.year = row[1]
            instance.summary = row[2]
            instance.employee_id = row[3]
        else:
            instance = cls(row[1], row[2], row[3])
            instance.id = review_id
            cls.all[review_id] = instance
        return instance
        pass
   

    @classmethod
    def find_by_id(cls, id):
        """Return a Review instance having the attribute values from the table row."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)
        else:
            return None
        pass

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        if self.id is None:
            raise ValueError("Cannot update a review that has not been saved.")
        sql = "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?"
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()
        pass

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""
        if self.id is None:
            raise ValueError("Cannot delete a review that has not been saved.")
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        if self.id in Review.all:
            del Review.all[self.id]
        self.id = None
        pass

    @classmethod
    def get_all(cls):
        """Return a list containing one Review instance per table row"""
        sql = "SELECT * FROM reviews"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]
        pass

 # year property: must be an integer >= 2000
    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int):
            raise ValueError("year must be an integer")
        if value < 2000:
            raise ValueError("year must be greater than or equal to 2000")
        self._year = value

 # summary property: must be a non-empty string
    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or len(value.strip()) == 0:
            raise ValueError("summary must be a non-empty string")
        self._summary = value

# employee_id property: must be the id of an existing Employee
    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # Import Employee here to avoid circular import issues.
        from employee import Employee
        if Employee.find_by_id(value) is None:
            raise ValueError("employee_id must refer to an existing Employee")
        self._employee_id = value