import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class LogLevel(Enum):
    """Log levels for generating logs"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogType(Enum):
    """Types of logs with different PI data patterns"""
    USER_REGISTRATION = "user_registration"
    USER_LOGIN = "user_login"
    TRANSACTION = "transaction"
    CUSTOMER_SERVICE = "customer_service"
    MEDICAL_RECORD = "medical_record"
    ERROR_REPORT = "error_report"
    AUDIT_LOG = "audit_log"


@dataclass
class LogEntry:
    """Represents a log entry with PI data"""
    timestamp: datetime
    level: LogLevel
    log_type: LogType
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class PIDataGenerator:
    """Generator for creating realistic PI data for testing"""
    
    # Sample data pools
    FIRST_NAMES = [
        "John", "Jane", "Michael", "Sarah", "Robert", "Emily", "David", "Jessica",
        "William", "Ashley", "Richard", "Amanda", "Joseph", "Melissa", "Thomas", "Stephanie"
    ]
    
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Wilson", "Anderson", "Taylor", "Thomas", "Moore", "Jackson"
    ]
    
    DOMAINS = [
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "example.com",
        "company.org", "university.edu", "government.gov", "bank.com", "healthcare.net"
    ]
    
    STREET_NAMES = [
        "Main St", "Oak Ave", "Elm St", "Maple Dr", "Cedar Ln", "Pine Rd",
        "Washington Blvd", "Lincoln Ave", "Park St", "First St"
    ]
    
    CITIES = [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
        "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville"
    ]
    
    @classmethod
    def generate_name(cls, include_title: bool = False) -> str:
        """Generate a random name"""
        first = random.choice(cls.FIRST_NAMES)
        last = random.choice(cls.LAST_NAMES)
        
        if include_title and random.random() < 0.3:
            title = random.choice(["Mr.", "Mrs.", "Ms.", "Dr."])
            return f"{title} {first} {last}"
        
        return f"{first} {last}"
    
    @classmethod
    def generate_email(cls, name: Optional[str] = None) -> str:
        """Generate a random email address"""
        if name:
            # Use provided name to create realistic email
            name_parts = name.split()
            if len(name_parts) >= 2:
                first = name_parts[0].lower()
                last = name_parts[-1].lower()
                
                # Different email formats
                formats = [
                    f"{first}.{last}",
                    f"{first}_{last}",
                    f"{first[0]}{last}",
                    f"{first}{last}",
                    f"{first}.{last[0]}"
                ]
                local = random.choice(formats)
            else:
                local = name.lower()
        else:
            # Generate random email
            first = random.choice(cls.FIRST_NAMES).lower()
            last = random.choice(cls.LAST_NAMES).lower()
            local = f"{first}.{last}"
        
        # Add random numbers sometimes
        if random.random() < 0.3:
            local += str(random.randint(1, 999))
        
        domain = random.choice(cls.DOMAINS)
        return f"{local}@{domain}"
    
    @classmethod
    def generate_phone(cls, us_format: bool = True) -> str:
        """Generate a random phone number"""
        if us_format:
            # US phone number
            area = random.randint(200, 999)
            exchange = random.randint(200, 999)
            number = random.randint(1000, 9999)
            
            formats = [
                f"({area}) {exchange}-{number}",
                f"{area}-{exchange}-{number}",
                f"{area}.{exchange}.{number}",
                f"+1-{area}-{exchange}-{number}"
            ]
            return random.choice(formats)
        else:
            # Indian phone number
            number = random.randint(6000000000, 9999999999)
            formats = [
                f"{str(number)[:5]}-{str(number)[5:]}",
                f"+91-{str(number)[:5]}-{str(number)[5:]}"
            ]
            return random.choice(formats)
    
    @classmethod
    def generate_dob(cls, age_range: tuple = (18, 80)) -> str:
        """Generate a random date of birth"""
        today = datetime.now()
        min_age, max_age = age_range
        
        # Generate random age within range
        age = random.randint(min_age, max_age)
        birth_year = today.year - age
        
        # Generate random month and day
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Use 28 to avoid month/day conflicts
        
        # Different date formats
        formats = [
            f"{month:02d}/{day:02d}/{birth_year}",
            f"{day:02d}-{month:02d}-{birth_year}",
            f"{birth_year}-{month:02d}-{day:02d}"
        ]
        return random.choice(formats)
    
    @classmethod
    def generate_ssn(cls) -> str:
        """Generate a random SSN (for testing only)"""
        area = random.randint(100, 899)  # Valid area numbers
        group = random.randint(10, 99)   # Valid group numbers
        serial = random.randint(1000, 9999)  # Valid serial numbers
        return f"{area:03d}-{group:02d}-{serial:04d}"
    
    @classmethod
    def generate_credit_card(cls) -> str:
        """Generate a random credit card number (for testing only)"""
        # Visa starts with 4, 13 or 16 digits
        if random.random() < 0.4:
            card_num = "4" + "".join([str(random.randint(0, 9)) for _ in range(15)])
        # MasterCard starts with 5, 16 digits
        elif random.random() < 0.7:
            card_num = "5" + str(random.randint(1, 5)) + "".join([str(random.randint(0, 9)) for _ in range(13)])
        # Amex starts with 3, 15 digits
        else:
            card_num = "3" + str(random.randint(4, 7)) + "".join([str(random.randint(0, 9)) for _ in range(12)])
        
        # Format with spaces
        formatted = f"{card_num[:4]} {card_num[4:8]} {card_num[8:12]} {card_num[12:]}"
        return formatted
    
    @classmethod
    def generate_address(cls) -> str:
        """Generate a random address"""
        number = random.randint(1, 9999)
        street = random.choice(cls.STREET_NAMES)
        city = random.choice(cls.CITIES)
        state = random.choice(["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"])
        zip_code = random.randint(10000, 99999)
        
        return f"{number} {street}, {city}, {state} {zip_code}"


class LogGenerator:
    """Generator for creating log entries with PI data"""
    
    def __init__(self):
        self.pi_generator = PIDataGenerator()
    
    def generate_log_entry(self, log_type: LogType, level: LogLevel = LogLevel.INFO) -> LogEntry:
        """Generate a single log entry with PI data"""
        timestamp = datetime.now() - timedelta(minutes=random.randint(0, 1440))
        session_id = self._generate_session_id()
        ip_address = self._generate_ip_address()
        
        if log_type == LogType.USER_REGISTRATION:
            message = self._generate_registration_message()
        elif log_type == LogType.USER_LOGIN:
            message = self._generate_login_message()
        elif log_type == LogType.TRANSACTION:
            message = self._generate_transaction_message()
        elif log_type == LogType.CUSTOMER_SERVICE:
            message = self._generate_customer_service_message()
        elif log_type == LogType.MEDICAL_RECORD:
            message = self._generate_medical_record_message()
        elif log_type == LogType.ERROR_REPORT:
            message = self._generate_error_report_message()
        elif log_type == LogType.AUDIT_LOG:
            message = self._generate_audit_log_message()
        else:
            message = "Generic log message"
        
        return LogEntry(
            timestamp=timestamp,
            level=level,
            log_type=log_type,
            message=message,
            session_id=session_id,
            ip_address=ip_address
        )
    
    def generate_log_batch(self, count: int, log_types: Optional[List[LogType]] = None) -> List[LogEntry]:
        """Generate a batch of log entries"""
        if log_types is None:
            log_types = list(LogType)
        
        logs = []
        for _ in range(count):
            log_type = random.choice(log_types)
            level = random.choice(list(LogLevel))
            logs.append(self.generate_log_entry(log_type, level))
        
        return logs
    
    def _generate_session_id(self) -> str:
        """Generate a random session ID"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    
    def _generate_ip_address(self) -> str:
        """Generate a random IP address"""
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    
    def _generate_registration_message(self) -> str:
        """Generate user registration log message"""
        name = self.pi_generator.generate_name(include_title=True)
        email = self.pi_generator.generate_email(name)
        phone = self.pi_generator.generate_phone()
        dob = self.pi_generator.generate_dob()
        address = self.pi_generator.generate_address()
        
        messages = [
            f"New user registration: {name}, Email: {email}, Phone: {phone}, DOB: {dob}, Address: {address}",
            f"User account created for {name} with email {email}. Contact: {phone}. Born: {dob}. Lives at {address}",
            f"Registration completed - Name: {name}, Email: {email}, Phone: {phone}, Date of Birth: {dob}, Address: {address}"
        ]
        
        return random.choice(messages)
    
    def _generate_login_message(self) -> str:
        """Generate user login log message"""
        email = self.pi_generator.generate_email()
        name = self.pi_generator.generate_name()
        ip = self._generate_ip_address()
        
        messages = [
            f"User login successful: {name} ({email}) from IP {ip}",
            f"Login attempt: {email} (Name: {name}) from {ip}",
            f"Authentication successful for {name} with email {email} from IP address {ip}"
        ]
        
        return random.choice(messages)
    
    def _generate_transaction_message(self) -> str:
        """Generate transaction log message"""
        name = self.pi_generator.generate_name()
        email = self.pi_generator.generate_email()
        credit_card = self.pi_generator.generate_credit_card()
        amount = f"${random.uniform(10.0, 1000.0):.2f}"
        
        messages = [
            f"Payment processed for {name} ({email}) - Amount: {amount} - Card: {credit_card}",
            f"Transaction completed: {amount} charged to {credit_card} for customer {name} ({email})",
            f"Payment of {amount} from {name} ({email}) using card ending in {credit_card[-4:]}"
        ]
        
        return random.choice(messages)
    
    def _generate_customer_service_message(self) -> str:
        """Generate customer service log message"""
        name = self.pi_generator.generate_name(include_title=True)
        email = self.pi_generator.generate_email(name)
        phone = self.pi_generator.generate_phone()
        ssn = self.pi_generator.generate_ssn()
        
        messages = [
            f"Customer support call: {name}, Email: {email}, Phone: {phone}, SSN: {ssn}",
            f"Support ticket created for {name} - Contact: {email}, {phone}. ID: {ssn}",
            f"Service request from {name} ({email}, {phone}) - Account SSN: {ssn}"
        ]
        
        return random.choice(messages)
    
    def _generate_medical_record_message(self) -> str:
        """Generate medical record log message"""
        name = self.pi_generator.generate_name(include_title=True)
        dob = self.pi_generator.generate_dob()
        ssn = self.pi_generator.generate_ssn()
        phone = self.pi_generator.generate_phone()
        
        messages = [
            f"Patient record accessed: {name}, DOB: {dob}, SSN: {ssn}, Contact: {phone}",
            f"Medical file opened for {name} - Born: {dob}, ID: {ssn}, Phone: {phone}",
            f"Healthcare record: Patient {name}, Date of Birth: {dob}, SSN: {ssn}, Emergency Contact: {phone}"
        ]
        
        return random.choice(messages)
    
    def _generate_error_report_message(self) -> str:
        """Generate error report log message"""
        name = self.pi_generator.generate_name()
        email = self.pi_generator.generate_email(name)
        phone = self.pi_generator.generate_phone()
        error_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        messages = [
            f"Error report submitted by {name} ({email}, {phone}) - Error ID: {error_id}",
            f"Bug report from {name} - Contact: {email}, {phone} - Reference: {error_id}",
            f"System error reported by user {name} ({email}) - Phone: {phone} - Case: {error_id}"
        ]
        
        return random.choice(messages)
    
    def _generate_audit_log_message(self) -> str:
        """Generate audit log message"""
        name = self.pi_generator.generate_name(include_title=True)
        email = self.pi_generator.generate_email(name)
        ssn = self.pi_generator.generate_ssn()
        action = random.choice(["accessed", "modified", "deleted", "created", "exported"])
        
        messages = [
            f"Audit: User {name} ({email}) {action} record with SSN {ssn}",
            f"Security audit: {name} ({email}) performed {action} action on sensitive data {ssn}",
            f"Audit trail: {name} with email {email} {action} file containing SSN {ssn}"
        ]
        
        return random.choice(messages)
    
    def format_log_entry(self, entry: LogEntry) -> str:
        """Format log entry as a string"""
        timestamp_str = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp_str}] {entry.level.value} - {entry.message}"
    
    def format_log_batch(self, entries: List[LogEntry]) -> List[str]:
        """Format a batch of log entries as strings"""
        return [self.format_log_entry(entry) for entry in entries]


class LogScenarioGenerator:
    """Generator for creating specific testing scenarios"""
    
    def __init__(self):
        self.log_generator = LogGenerator()
    
    def generate_compliance_test_scenario(self) -> List[str]:
        """Generate logs specifically for compliance testing"""
        scenarios = []
        
        # GDPR scenario - multiple PI types
        gdpr_logs = [
            "User registration: John Smith, Email: john.smith@gmail.com, Phone: (555) 123-4567, DOB: 01/15/1990",
            "Customer data: Mrs. Jane Johnson (jane.j@yahoo.com), SSN: 123-45-6789, Address: 123 Main St, New York, NY 10001",
            "Transaction: Dr. Robert Williams paid $500.00 using credit card 4111111111111111, email: dr.williams@hospital.org"
        ]
        scenarios.extend(gdpr_logs)
        
        # HIPAA scenario - medical data
        hipaa_logs = [
            "Patient record: Sarah Brown, DOB: 03/22/1985, SSN: 987-65-4321, Phone: (212) 555-0123",
            "Medical appointment: Emily Davis (emily.davis@email.com), DOB: 07/10/1992, Insurance: 4222222222222222",
            "Healthcare access: Dr. Michael Miller reviewed patient Thomas Wilson, SSN: 456-78-9012, DOB: 12/01/1978"
        ]
        scenarios.extend(hipaa_logs)
        
        # PCI DSS scenario - payment data
        pci_logs = [
            "Payment processed: Card ending in 1234, Amount: $99.99, Customer: Alex Johnson, Email: alex@business.com",
            "Transaction failed: Credit card 5555555555554444 declined for user Jessica Smith (jessica@company.org)",
            "Refund issued: $250.00 to card 378282246310005, Customer: William Brown, Phone: (800) 555-0199"
        ]
        scenarios.extend(pci_logs)
        
        return scenarios
    
    def generate_edge_case_scenario(self) -> List[str]:
        """Generate logs with edge cases and difficult-to-detect PI"""
        edge_cases = [
            # Partially masked PI that should still be detected
            "User: j***@gmail.com, Phone: (555) ***-4567, Name: J*** Smith",
            
            # PI in different formats
            "Contact: john.doe+tag@sub.domain.co.uk, Tel: +1-555-123-4567, DOB: 1990-01-15",
            
            # Mixed case and special characters
            "CUSTOMER: John.O'Doe@Example.COM, PHONE: (555) 123.4567, BIRTH: 01-15-1990",
            
            # International formats
            "Client: Jean Dupont, Email: jean.dupont@france.fr, Tel: +33-1-23-45-67-89, DOB: 15/01/1990",
            
            # Embedded PI
            "Error processing payment for John Smith (john.smith@company.com) using card 4111111111111111",
            
            # Multiple PI in single message
            "User registration complete: Dr. Alice Johnson, Email: alice@hospital.edu, Phone: (555) 123-4567, DOB: 12/25/1980, SSN: 123-45-6789, Card: 5555555555554444"
        ]
        
        return edge_cases
    
    def generate_performance_test_scenario(self, count: int = 1000) -> List[str]:
        """Generate a large number of logs for performance testing"""
        entries = self.log_generator.generate_log_batch(count)
        return self.log_generator.format_log_batch(entries)
    
    def generate_false_positive_scenario(self) -> List[str]:
        """Generate logs that might trigger false positives"""
        false_positives = [
            # Technical data that looks like PI
            "System error: Code 123-45-6789 failed at line 555-123-4567",
            "Configuration: email.server@localhost, phone.gateway@192.168.1.1",
            "Date format: 2023-12-25 matches pattern MM/DD/YYYY",
            "Version: v1.2.3-4567, Build: 1234567890123456",
            
            # Common patterns that aren't PI
            "Email sent to support@company.com from system@notification.service",
            "Phone extension: 123-4567 (internal), Building: 411, Room: 1111",
            "Date: 12/25/2023 (Christmas), Time: 12:25:00",
            
            # Product codes and identifiers
            "Product SKU: EMAIL-123, Phone Model: XYZ-456, Customer ID: DOB-789"
        ]
        
        return false_positives
