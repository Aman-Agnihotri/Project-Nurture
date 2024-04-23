import {
    Button,
    Container,
    Heading,
    Input,
    VStack,
} from '@chakra-ui/react';
import { useState } from 'react';

const Form = () => {
    const [formData, setFormData] = useState({
        name: '',
        age: '',
        address: '',
        bmi: '',
        height: '',
        weight: ''
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // Here you can perform actions with the form data, such as sending it to a backend server
        console.log(formData);
    };

    return (
        <Container maxW={'container.xl'} h={'120vh'} p={'16'} display={'flex'} justifyContent={'center'}>
            <form onSubmit={handleSubmit}>
                <VStack
                    alignItems={'stretch'}
                    spacing={'8'}
                    w={['full', '96']}
                    m={'auto'}
                    my={'16'}
                >
                    <Heading>Fill in your Details</Heading>

                    <Input
                        name="name"
                        placeholder={'Name'}
                        type={'text'}
                        value={formData.name}
                        onChange={handleChange}
                        required
                        focusBorderColor={'teal.500'}
                    />
                    <Input
                        name="age"
                        placeholder={'Age'}
                        type={'number'}
                        value={formData.age}
                        onChange={handleChange}
                        required
                        focusBorderColor={'teal.500'}
                    />
                    <Input
                        name="address"
                        placeholder={'Address'}
                        type={'text'}
                        value={formData.address}
                        onChange={handleChange}
                        required
                        focusBorderColor={'teal.500'}
                    />
                    
                    <Input
                        name="bmi"
                        placeholder={'BMI Index'}
                        type={'text'}
                        value={formData.bmi}
                        onChange={handleChange}
                        required
                        focusBorderColor={'teal.500'}
                    />
                    <Input
                        name="height"
                        placeholder={'Height'}
                        type={'text'}
                        value={formData.height}
                        onChange={handleChange}
                        required
                        focusBorderColor={'teal.500'}
                    />
                    <Input
                        name="weight"
                        placeholder={'Weight'}
                        type={'text'}
                        value={formData.weight}
                        onChange={handleChange}
                        required
                        focusBorderColor={'teal.500'}
                    />
                   <Button colorScheme={'teal'} type={'submit'}>
                        Submit
                    </Button>
                </VStack>
            </form>
        </Container>
    );
};

export default Form;