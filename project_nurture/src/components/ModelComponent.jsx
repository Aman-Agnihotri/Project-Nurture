import { Container, VStack, Heading, Input, Select, Button } from '@chakra-ui/react';
import { useState } from 'react';

const ModelComponent = () => {
    const [inputValues, setInputValues] = useState({
        "Age (1-11)": '',
        "Weight (kg)": '',
        "Height (cm)": '',
        "Household Income": '',
        "Health Portfolio": '',
        "Urban or Rural": ''
    });
    const [result, setResult] = useState('');

    const handleInputChange = (e) => {
        setInputValues({
            ...inputValues,
            [e.target.name]: e.target.value
        });
    };

    const handleFormSubmit = (e) => {
        e.preventDefault();
        if (inputValues["Health Portfolio"] === '' || inputValues["Urban or Rural"] === '') {
            alert('Please select all options');
            return;
        }
        fetch('http://localhost:8000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(inputValues)
        })
            .then(response => response.json())
            .then(data => setResult(data.prediction))
            .catch(error => console.error(error)); 
        };

    return (
        <Container maxW={'container.xl'} p='16'>
            <VStack
                alignItems={'stretch'}
                spacing={'8'}
                w={['full', '96']}
                m={'auto'}
                my={'16'}
            >
                <Heading>Predictive Model Input</Heading>
                <form onSubmit={handleFormSubmit}>
                    <Input
                        type="number"
                        name="Age (1-11)"
                        value={inputValues["Age (1-11)"]}
                        onChange={handleInputChange}
                        placeholder="Age (1-11)"
                        required
                        focusBorderColor={'teal.500'}
                    />
                    <Input
                        type="number"
                        name="Weight (kg)"
                        value={inputValues["Weight (kg)"]}
                        onChange={handleInputChange}
                        placeholder="Weight (kg)"
                        required
                        focusBorderColor={'teal.500'}
                    />
                    <Input
                        type="number"
                        name="Height (cm)"
                        value={inputValues["Height (cm)"]}
                        onChange={handleInputChange}
                        placeholder="Height (cm)"
                        required
                        focusBorderColor={'teal.500'}
                    />
                    <Input
                        type="number"
                        name="Household Income"
                        value={inputValues["Household Income"]}
                        onChange={handleInputChange}
                        placeholder="Household Income"
                        required
                        focusBorderColor={'teal.500'}
                    />
                    <Select
                        name="Health Portfolio"
                        value={inputValues["Health Portfolio"]}
                        onChange={handleInputChange}
                        placeholder="Health Portfolio"
                        required
                        focusBorderColor={'teal.500'}
                    >
                        <option value="Good">Good</option>
                        <option value="Average">Average</option>
                        <option value="Poor">Poor</option>
                    </Select>
                    <Select
                        name="Urban or Rural"
                        value={inputValues["Urban or Rural"]}
                        onChange={handleInputChange}
                        placeholder="Urban or Rural"
                        required
                        focusBorderColor={'teal.500'}
                    >
                        <option value="Urban">Urban</option>
                        <option value="Rural">Rural</option>
                    </Select>
                    <Button colorScheme={'teal'} type="submit">Predict</Button>
                </form>
                <Heading>Prediction</Heading>
                <p>{result}</p>
            </VStack>
        </Container>
    );
};

export default ModelComponent;